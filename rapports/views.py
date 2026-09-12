from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import (
    ExploitationForm,
    FicheVaccinationEauBoissonForm,
    FicheVaccinationInjectionForm,
    PeseeIndividuelleFormSet,
    PeseeQuotidienneOeufsForm,
    PoidsHebdomadaireForm,
)
from .models import (
    Exploitation,
    FicheVaccinationEauBoisson,
    FicheVaccinationInjection,
    PeseeQuotidienneOeufs,
    PoidsHebdomadaire,
)
from .utils import render_to_pdf


# ---------------------------------------------------------------------------
# Aide : exploitation actuellement sélectionnée par l'utilisateur connecté
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Aide : filtrage par mois ou par période (date début / date fin) via GET
# ---------------------------------------------------------------------------
def filtrer_par_periode(request, queryset, champ_date="date"):
    """
    Applique sur `queryset` les filtres présents dans la requête GET :
    - ?mois=YYYY-MM              -> filtre sur le mois entier
    - ?date_debut=YYYY-MM-DD     -> filtre à partir de cette date
    - ?date_fin=YYYY-MM-DD       -> filtre jusqu'à cette date
    Le filtre "mois" est prioritaire s'il est renseigné.
    """
    mois = request.GET.get("mois")
    date_debut = request.GET.get("date_debut")
    date_fin = request.GET.get("date_fin")

    if mois:
        try:
            annee, m = mois.split("-")
            queryset = queryset.filter(**{
                f"{champ_date}__year": int(annee),
                f"{champ_date}__month": int(m),
            })
        except (ValueError, AttributeError):
            pass
    else:
        if date_debut:
            queryset = queryset.filter(**{f"{champ_date}__gte": date_debut})
        if date_fin:
            queryset = queryset.filter(**{f"{champ_date}__lte": date_fin})

    return queryset


def get_exploitation_courante(request):
    exploitation_id = request.session.get("exploitation_id")
    qs = Exploitation.objects.filter(proprietaire=request.user)
    if exploitation_id:
        exploitation = qs.filter(pk=exploitation_id).first()
        if exploitation:
            return exploitation
    exploitation = qs.first()
    if exploitation:
        request.session["exploitation_id"] = exploitation.pk
    return exploitation


# ---------------------------------------------------------------------------
# Tableau de bord
# ---------------------------------------------------------------------------
@login_required
def accueil(request):
    exploitation = get_exploitation_courante(request)
    contexte = {"exploitation": exploitation}

    if exploitation:
        contexte.update(
            {
                "nb_vaccins_eau": FicheVaccinationEauBoisson.objects.filter(
                    exploitation=exploitation
                ).count(),
                "nb_vaccins_injection": FicheVaccinationInjection.objects.filter(
                    exploitation=exploitation
                ).count(),
                "nb_semaines_poids": PoidsHebdomadaire.objects.filter(
                    exploitation=exploitation
                ).count(),
                "nb_pesees_oeufs": PeseeQuotidienneOeufs.objects.filter(
                    exploitation=exploitation
                ).count(),
                "dernieres_vaccinations_eau": FicheVaccinationEauBoisson.objects.filter(
                    exploitation=exploitation
                )[:5],
                "dernieres_vaccinations_injection": FicheVaccinationInjection.objects.filter(
                    exploitation=exploitation
                )[:5],
                "dernieres_pesees_oeufs": PeseeQuotidienneOeufs.objects.filter(
                    exploitation=exploitation
                )[:5],
            }
        )
    return render(request, "rapports/accueil.html", contexte)


# ---------------------------------------------------------------------------
# Exploitations
# ---------------------------------------------------------------------------
@login_required
def liste_exploitations(request):
    exploitations = Exploitation.objects.filter(proprietaire=request.user)
    return render(request, "rapports/exploitation_list.html", {"exploitations": exploitations})


@login_required
def creer_exploitation(request):
    if request.method == "POST":
        form = ExploitationForm(request.POST, request.FILES)
        if form.is_valid():
            exploitation = form.save(commit=False)
            exploitation.proprietaire = request.user
            exploitation.save()
            request.session["exploitation_id"] = exploitation.pk
            messages.success(request, "Exploitation créée avec succès.")
            return redirect("accueil")
    else:
        form = ExploitationForm()
    return render(request, "rapports/exploitation_form.html", {"form": form, "titre": "Nouvelle exploitation"})


@login_required
def modifier_exploitation(request, pk):
    exploitation = get_object_or_404(Exploitation, pk=pk, proprietaire=request.user)
    if request.method == "POST":
        form = ExploitationForm(request.POST, request.FILES, instance=exploitation)
        if form.is_valid():
            form.save()
            messages.success(request, "Exploitation mise à jour.")
            return redirect("exploitation_list")
    else:
        form = ExploitationForm(instance=exploitation)
    return render(request, "rapports/exploitation_form.html", {"form": form, "titre": "Modifier l'exploitation", "exploitation_a_modifier": exploitation})


@login_required
def choisir_exploitation(request, pk):
    exploitation = get_object_or_404(Exploitation, pk=pk, proprietaire=request.user)
    request.session["exploitation_id"] = exploitation.pk
    messages.info(request, f"Exploitation active : {exploitation.nom}")
    return redirect("accueil")


# ---------------------------------------------------------------------------
# Vaccination — eau de boisson
# ---------------------------------------------------------------------------
@login_required
def vaccination_eau_list(request):
    exploitation = get_exploitation_courante(request)
    fiches = FicheVaccinationEauBoisson.objects.filter(exploitation=exploitation) if exploitation else FicheVaccinationEauBoisson.objects.none()
    fiches = filtrer_par_periode(request, fiches)
    return render(request, "rapports/vaccination_eau_list.html", {"fiches": fiches, "exploitation": exploitation})


@login_required
def vaccination_eau_detail(request, pk):
    fiche = get_object_or_404(FicheVaccinationEauBoisson, pk=pk, exploitation__proprietaire=request.user)
    return render(request, "rapports/vaccination_eau_detail.html", {"fiche": fiche})


def _prochain_numero_fiche(model, exploitation):
    """Calcule automatiquement le prochain N° de fiche pour cette exploitation."""
    dernier = model.objects.filter(exploitation=exploitation).aggregate(models.Max("numero_fiche"))
    return (dernier["numero_fiche__max"] or 0) + 1


@login_required
def vaccination_eau_create(request):
    exploitation = get_exploitation_courante(request)
    if not exploitation:
        messages.warning(request, "Créez d'abord une exploitation.")
        return redirect("exploitation_creer")
    if request.method == "POST":
        form = FicheVaccinationEauBoissonForm(request.POST, request.FILES)
        if form.is_valid():
            fiche = form.save(commit=False)
            fiche.exploitation = exploitation
            fiche.numero_fiche = _prochain_numero_fiche(FicheVaccinationEauBoisson, exploitation)
            fiche.save()
            messages.success(request, "Fiche de vaccination (eau de boisson) enregistrée.")
            return redirect("vaccination_eau_detail", pk=fiche.pk)
    else:
        form = FicheVaccinationEauBoissonForm()
    return render(request, "rapports/vaccination_eau_form.html", {"form": form, "titre": "Nouvelle fiche — Eau de boisson"})


@login_required
def vaccination_eau_update(request, pk):
    fiche = get_object_or_404(FicheVaccinationEauBoisson, pk=pk, exploitation__proprietaire=request.user)
    if request.method == "POST":
        form = FicheVaccinationEauBoissonForm(request.POST, request.FILES, instance=fiche)
        if form.is_valid():
            form.save()
            messages.success(request, "Fiche mise à jour.")
            return redirect("vaccination_eau_detail", pk=fiche.pk)
    else:
        form = FicheVaccinationEauBoissonForm(instance=fiche)
    return render(request, "rapports/vaccination_eau_form.html", {"form": form, "titre": "Modifier la fiche", "fiche": fiche})


@login_required
def vaccination_eau_delete(request, pk):
    fiche = get_object_or_404(FicheVaccinationEauBoisson, pk=pk, exploitation__proprietaire=request.user)
    if request.method == "POST":
        fiche.delete()
        messages.success(request, "Fiche supprimée.")
        return redirect("vaccination_eau_list")
    return render(request, "rapports/confirmer_suppression.html", {"objet": fiche})


# ---------------------------------------------------------------------------
# Vaccination — injection
# ---------------------------------------------------------------------------
@login_required
def vaccination_injection_list(request):
    exploitation = get_exploitation_courante(request)
    fiches = FicheVaccinationInjection.objects.filter(exploitation=exploitation) if exploitation else FicheVaccinationInjection.objects.none()
    fiches = filtrer_par_periode(request, fiches)
    return render(request, "rapports/vaccination_injection_list.html", {"fiches": fiches, "exploitation": exploitation})


@login_required
def vaccination_injection_detail(request, pk):
    fiche = get_object_or_404(FicheVaccinationInjection, pk=pk, exploitation__proprietaire=request.user)
    return render(request, "rapports/vaccination_injection_detail.html", {"fiche": fiche})


@login_required
def vaccination_injection_create(request):
    exploitation = get_exploitation_courante(request)
    if not exploitation:
        messages.warning(request, "Créez d'abord une exploitation.")
        return redirect("exploitation_creer")
    if request.method == "POST":
        form = FicheVaccinationInjectionForm(request.POST, request.FILES)
        if form.is_valid():
            fiche = form.save(commit=False)
            fiche.exploitation = exploitation
            fiche.numero_fiche = _prochain_numero_fiche(FicheVaccinationInjection, exploitation)
            fiche.save()
            messages.success(request, "Fiche de vaccination (injection) enregistrée.")
            return redirect("vaccination_injection_detail", pk=fiche.pk)
    else:
        form = FicheVaccinationInjectionForm()
    return render(request, "rapports/vaccination_injection_form.html", {"form": form, "titre": "Nouvelle fiche — Injection"})


@login_required
def vaccination_injection_update(request, pk):
    fiche = get_object_or_404(FicheVaccinationInjection, pk=pk, exploitation__proprietaire=request.user)
    if request.method == "POST":
        form = FicheVaccinationInjectionForm(request.POST, request.FILES, instance=fiche)
        if form.is_valid():
            form.save()
            messages.success(request, "Fiche mise à jour.")
            return redirect("vaccination_injection_detail", pk=fiche.pk)
    else:
        form = FicheVaccinationInjectionForm(instance=fiche)
    return render(request, "rapports/vaccination_injection_form.html", {"form": form, "titre": "Modifier la fiche", "fiche": fiche})


@login_required
def vaccination_injection_delete(request, pk):
    fiche = get_object_or_404(FicheVaccinationInjection, pk=pk, exploitation__proprietaire=request.user)
    if request.method == "POST":
        fiche.delete()
        messages.success(request, "Fiche supprimée.")
        return redirect("vaccination_injection_list")
    return render(request, "rapports/confirmer_suppression.html", {"objet": fiche})


# ---------------------------------------------------------------------------
# Poids hebdomadaire visé
# ---------------------------------------------------------------------------
@login_required
def poids_semaine_list(request):
    exploitation = get_exploitation_courante(request)
    semaines = PoidsHebdomadaire.objects.filter(exploitation=exploitation) if exploitation else PoidsHebdomadaire.objects.none()
    semaines = filtrer_par_periode(request, semaines)
    return render(request, "rapports/poids_semaine_list.html", {"semaines": semaines, "exploitation": exploitation})


@login_required
def poids_semaine_detail(request, pk):
    semaine = get_object_or_404(PoidsHebdomadaire, pk=pk, exploitation__proprietaire=request.user)
    return render(request, "rapports/poids_semaine_detail.html", {"semaine": semaine})


@login_required
def poids_semaine_create(request):
    exploitation = get_exploitation_courante(request)
    if not exploitation:
        messages.warning(request, "Créez d'abord une exploitation.")
        return redirect("exploitation_creer")

    if request.method == "POST":
        form = PoidsHebdomadaireForm(request.POST)
        formset = PeseeIndividuelleFormSet(request.POST, instance=PoidsHebdomadaire())
        if form.is_valid():
            semaine = form.save(commit=False)
            semaine.exploitation = exploitation
            semaine.save()
            formset = PeseeIndividuelleFormSet(request.POST, instance=semaine)
            if formset.is_valid():
                formset.save()
                messages.success(request, "Semaine de pesée enregistrée.")
                return redirect("poids_semaine_detail", pk=semaine.pk)
    else:
        form = PoidsHebdomadaireForm()
        formset = PeseeIndividuelleFormSet(instance=PoidsHebdomadaire())

    return render(
        request,
        "rapports/poids_semaine_form.html",
        {"form": form, "formset": formset, "titre": "Nouvelle semaine de pesée"},
    )


@login_required
def poids_semaine_update(request, pk):
    semaine = get_object_or_404(PoidsHebdomadaire, pk=pk, exploitation__proprietaire=request.user)
    if request.method == "POST":
        form = PoidsHebdomadaireForm(request.POST, instance=semaine)
        formset = PeseeIndividuelleFormSet(request.POST, instance=semaine)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Semaine de pesée mise à jour.")
            return redirect("poids_semaine_detail", pk=semaine.pk)
    else:
        form = PoidsHebdomadaireForm(instance=semaine)
        formset = PeseeIndividuelleFormSet(instance=semaine)
    return render(
        request,
        "rapports/poids_semaine_form.html",
        {"form": form, "formset": formset, "titre": "Modifier la semaine"},
    )


@login_required
def poids_semaine_delete(request, pk):
    semaine = get_object_or_404(PoidsHebdomadaire, pk=pk, exploitation__proprietaire=request.user)
    if request.method == "POST":
        semaine.delete()
        messages.success(request, "Semaine supprimée.")
        return redirect("poids_semaine_list")
    return render(request, "rapports/confirmer_suppression.html", {"objet": semaine})


# ---------------------------------------------------------------------------
# Pesée quotidienne des œufs
# ---------------------------------------------------------------------------
@login_required
def pesee_oeufs_list(request):
    exploitation = get_exploitation_courante(request)
    pesees = PeseeQuotidienneOeufs.objects.filter(exploitation=exploitation) if exploitation else PeseeQuotidienneOeufs.objects.none()
    pesees = filtrer_par_periode(request, pesees)
    return render(request, "rapports/pesee_oeufs_list.html", {"pesees": pesees, "exploitation": exploitation})


@login_required
def pesee_oeufs_create(request):
    exploitation = get_exploitation_courante(request)
    if not exploitation:
        messages.warning(request, "Créez d'abord une exploitation.")
        return redirect("exploitation_creer")
    if request.method == "POST":
        form = PeseeQuotidienneOeufsForm(request.POST)
        if form.is_valid():
            pesee = form.save(commit=False)
            pesee.exploitation = exploitation
            pesee.save()
            messages.success(request, "Pesée du jour enregistrée.")
            return redirect("pesee_oeufs_list")
    else:
        form = PeseeQuotidienneOeufsForm()
    return render(request, "rapports/pesee_oeufs_form.html", {"form": form, "titre": "Nouvelle pesée d'œufs"})


@login_required
def pesee_oeufs_delete(request, pk):
    pesee = get_object_or_404(PeseeQuotidienneOeufs, pk=pk, exploitation__proprietaire=request.user)
    if request.method == "POST":
        pesee.delete()
        messages.success(request, "Pesée supprimée.")
        return redirect("pesee_oeufs_list")
    return render(request, "rapports/confirmer_suppression.html", {"objet": pesee})


# ---------------------------------------------------------------------------
# Impression et téléchargement PDF des fiches (format A4)
# ---------------------------------------------------------------------------
@login_required
def vaccination_eau_imprimer(request, pk):
    fiche = get_object_or_404(FicheVaccinationEauBoisson, pk=pk, exploitation__proprietaire=request.user)
    return render(request, "rapports/print/vaccination_eau.html", {"fiche": fiche, "exploitation": fiche.exploitation})


@login_required
def vaccination_eau_pdf(request, pk):
    fiche = get_object_or_404(FicheVaccinationEauBoisson, pk=pk, exploitation__proprietaire=request.user)
    nom = f"fiche_vaccination_eau_{fiche.numero_fiche}.pdf"
    return render_to_pdf(
        "rapports/print/vaccination_eau.html",
        {"fiche": fiche, "exploitation": fiche.exploitation},
        nom_fichier=nom,
    )


@login_required
def vaccination_injection_imprimer(request, pk):
    fiche = get_object_or_404(FicheVaccinationInjection, pk=pk, exploitation__proprietaire=request.user)
    return render(request, "rapports/print/vaccination_injection.html", {"fiche": fiche, "exploitation": fiche.exploitation})


@login_required
def vaccination_injection_pdf(request, pk):
    fiche = get_object_or_404(FicheVaccinationInjection, pk=pk, exploitation__proprietaire=request.user)
    nom = f"fiche_vaccination_injection_{fiche.numero_fiche}.pdf"
    return render_to_pdf(
        "rapports/print/vaccination_injection.html",
        {"fiche": fiche, "exploitation": fiche.exploitation},
        nom_fichier=nom,
    )


def _contexte_grille_poids(semaine):
    """
    Construit la grille 21 x 18 telle qu'elle est remplie sur la fiche papier :
    les pesées sont placées dans l'ordre de saisie en remplissant d'abord
    entièrement la ligne 1 (18 cases), puis la ligne 2, etc.
    """
    pesees = list(semaine.pesees.all().order_by("numero_sujet"))
    NB_COLONNES = 18
    NB_LIGNES = 21

    grille = {i: {} for i in range(1, NB_LIGNES + 1)}
    for position, pesee in enumerate(pesees, start=1):
        ligne = ((position - 1) // NB_COLONNES) + 1
        colonne = ((position - 1) % NB_COLONNES) + 1
        if ligne <= NB_LIGNES:
            grille[ligne][colonne] = pesee.poids_grammes

    lignes = [
        {"numero": i, "valeurs": [grille[i].get(c) for c in range(1, NB_COLONNES + 1)]}
        for i in range(1, NB_LIGNES + 1)
    ]

    return {
        "semaine": semaine,
        "exploitation": semaine.exploitation,
        "colonnes": range(1, NB_COLONNES + 1),
        "lignes": lignes,
    }


@login_required
def poids_semaine_imprimer(request, pk):
    semaine = get_object_or_404(PoidsHebdomadaire, pk=pk, exploitation__proprietaire=request.user)
    return render(request, "rapports/print/poids_semaine.html", _contexte_grille_poids(semaine))


@login_required
def poids_semaine_pdf(request, pk):
    semaine = get_object_or_404(PoidsHebdomadaire, pk=pk, exploitation__proprietaire=request.user)
    nom = f"poids_semaine_{semaine.semaine_numero}.pdf"
    return render_to_pdf("rapports/print/poids_semaine.html", _contexte_grille_poids(semaine), nom_fichier=nom)


@login_required
def pesee_oeufs_imprimer(request):
    exploitation = get_exploitation_courante(request)
    pesees = PeseeQuotidienneOeufs.objects.filter(exploitation=exploitation) if exploitation else PeseeQuotidienneOeufs.objects.none()
    pesees = filtrer_par_periode(request, pesees)
    return render(request, "rapports/print/pesee_oeufs.html", {"pesees": pesees, "exploitation": exploitation})


@login_required
def pesee_oeufs_pdf(request):
    exploitation = get_exploitation_courante(request)
    pesees = PeseeQuotidienneOeufs.objects.filter(exploitation=exploitation) if exploitation else PeseeQuotidienneOeufs.objects.none()
    pesees = filtrer_par_periode(request, pesees)
    return render_to_pdf(
        "rapports/print/pesee_oeufs.html",
        {"pesees": pesees, "exploitation": exploitation},
        nom_fichier="pesees_oeufs.pdf",
    )


# ---------------------------------------------------------------------------
# Impression / PDF des historiques complets (avec filtre période/mois)
# ---------------------------------------------------------------------------
@login_required
def vaccination_eau_liste_imprimer(request):
    exploitation = get_exploitation_courante(request)
    fiches = FicheVaccinationEauBoisson.objects.filter(exploitation=exploitation) if exploitation else FicheVaccinationEauBoisson.objects.none()
    fiches = filtrer_par_periode(request, fiches)
    return render(request, "rapports/print/vaccination_eau_liste.html", {"fiches": fiches, "exploitation": exploitation})


@login_required
def vaccination_eau_liste_pdf(request):
    exploitation = get_exploitation_courante(request)
    fiches = FicheVaccinationEauBoisson.objects.filter(exploitation=exploitation) if exploitation else FicheVaccinationEauBoisson.objects.none()
    fiches = filtrer_par_periode(request, fiches)
    return render_to_pdf(
        "rapports/print/vaccination_eau_liste.html",
        {"fiches": fiches, "exploitation": exploitation},
        nom_fichier="historique_vaccination_eau.pdf",
    )


@login_required
def vaccination_injection_liste_imprimer(request):
    exploitation = get_exploitation_courante(request)
    fiches = FicheVaccinationInjection.objects.filter(exploitation=exploitation) if exploitation else FicheVaccinationInjection.objects.none()
    fiches = filtrer_par_periode(request, fiches)
    return render(request, "rapports/print/vaccination_injection_liste.html", {"fiches": fiches, "exploitation": exploitation})


@login_required
def vaccination_injection_liste_pdf(request):
    exploitation = get_exploitation_courante(request)
    fiches = FicheVaccinationInjection.objects.filter(exploitation=exploitation) if exploitation else FicheVaccinationInjection.objects.none()
    fiches = filtrer_par_periode(request, fiches)
    return render_to_pdf(
        "rapports/print/vaccination_injection_liste.html",
        {"fiches": fiches, "exploitation": exploitation},
        nom_fichier="historique_vaccination_injection.pdf",
    )


@login_required
def poids_semaine_liste_imprimer(request):
    exploitation = get_exploitation_courante(request)
    semaines = PoidsHebdomadaire.objects.filter(exploitation=exploitation) if exploitation else PoidsHebdomadaire.objects.none()
    semaines = filtrer_par_periode(request, semaines)
    return render(request, "rapports/print/poids_semaine_liste.html", {"semaines": semaines, "exploitation": exploitation})


@login_required
def poids_semaine_liste_pdf(request):
    exploitation = get_exploitation_courante(request)
    semaines = PoidsHebdomadaire.objects.filter(exploitation=exploitation) if exploitation else PoidsHebdomadaire.objects.none()
    semaines = filtrer_par_periode(request, semaines)
    return render_to_pdf(
        "rapports/print/poids_semaine_liste.html",
        {"semaines": semaines, "exploitation": exploitation},
        nom_fichier="historique_poids_semaines.pdf",
    )
