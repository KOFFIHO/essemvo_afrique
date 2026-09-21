from django import forms
from django.forms import inlineformset_factory

from .models import (
    Exploitation,
    FicheVaccinationEauBoisson,
    FicheVaccinationInjection,
    PeseeIndividuelle,
    PeseeQuotidienneOeufs,
    PoidsHebdomadaire,
    RapportJournalier,
)

# ---------------------------------------------------------------------------
# Champs date/heure "sûrs" pour les widgets HTML5 (date, time, datetime-local)
# ---------------------------------------------------------------------------
# Avec le site en français (LANGUAGE_CODE = "fr-fr"), Django formate par
# défaut les dates/heures existantes selon le format localisé (ex. JJ/MM/AAAA)
# pour les réafficher dans un formulaire de modification. Or les champs HTML5
# <input type="date">/"time"/"datetime-local"> exigent STRICTEMENT le format
# ISO (AAAA-MM-JJ, HH:MM, AAAA-MM-JJTHH:MM), quelle que soit la langue.
# Résultat sans ce correctif : la valeur existante ne s'affiche plus du tout
# en modification (le navigateur ne reconnaît pas le format reçu), même si
# elle est bien enregistrée en base.
#
# Ces trois fonctions forcent explicitement le format ISO, à la fois pour
# l'affichage (widget) ET pour la lecture du formulaire soumis (input_formats),
# et doivent être utilisées pour TOUT champ date/heure/date-heure du site.

FORMAT_DATE = "%Y-%m-%d"
FORMAT_HEURE = "%H:%M"
FORMAT_DATE_HEURE = "%Y-%m-%dT%H:%M"


def champ_date(label=None, required=True, **kwargs):
    return forms.DateField(
        label=label,
        required=required,
        input_formats=[FORMAT_DATE],
        widget=forms.DateInput(attrs={"type": "date"}, format=FORMAT_DATE),
        **kwargs,
    )


def champ_heure(label=None, required=True, **kwargs):
    return forms.TimeField(
        label=label,
        required=required,
        input_formats=[FORMAT_HEURE],
        widget=forms.TimeInput(attrs={"type": "time"}, format=FORMAT_HEURE),
        **kwargs,
    )


def champ_date_heure(label=None, required=True, **kwargs):
    return forms.DateTimeField(
        label=label,
        required=required,
        input_formats=[FORMAT_DATE_HEURE],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}, format=FORMAT_DATE_HEURE),
        **kwargs,
    )


class BootstrapFormMixin:
    """Ajoute automatiquement la classe Bootstrap `form-control` à chaque champ."""

    def _bootstrapper(self):
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.CheckboxInput,)):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", "form-control")


class ExploitationForm(BootstrapFormMixin, forms.ModelForm):
    date_arrivee_sujets = champ_date_heure(
        label="Date et heure d'arrivée des sujets",
        required=False,
        help_text="Sert à calculer automatiquement l'âge des sujets (en jours) sur toutes les fiches.",
    )

    class Meta:
        model = Exploitation
        fields = ["nom", "logo", "localisation", "effectif_initial", "date_arrivee_sujets"]
        widgets = {
            "logo": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrapper()


class FicheVaccinationEauBoissonForm(BootstrapFormMixin, forms.ModelForm):
    date = champ_date(label="Date")
    date_validite_vaccin = champ_date(label="Date de validité du vaccin")
    heure_assoiffement_debut = champ_heure(label="Heure d'assoiffement — début")
    heure_assoiffement_fin = champ_heure(label="Heure d'assoiffement — fin")
    heure_abreuvement_debut = champ_heure(label="Heure d'abreuvement — début")
    heure_abreuvement_fin = champ_heure(label="Heure d'abreuvement — fin")

    class Meta:
        model = FicheVaccinationEauBoisson
        # numero_fiche est calculé automatiquement (voir la vue de création) : jamais dans le formulaire.
        # Les images d'étiquette sont gérées séparément (upload multiple, voir la vue).
        exclude = ["exploitation", "cree_le", "numero_fiche"]
        widgets = {
            "observations": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrapper()


class FicheVaccinationInjectionForm(BootstrapFormMixin, forms.ModelForm):
    date = champ_date(label="Date")
    date_validite_vaccin = champ_date(label="Date de validité du vaccin")
    heure_debut = champ_heure(label="Heure de début (injection)")
    heure_fin = champ_heure(label="Heure de fin (injection)")

    class Meta:
        model = FicheVaccinationInjection
        # numero_fiche est calculé automatiquement (voir la vue de création) : jamais dans le formulaire.
        # Les images d'étiquette sont gérées séparément (upload multiple, voir la vue).
        exclude = ["exploitation", "cree_le", "numero_fiche"]
        widgets = {
            "observations": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrapper()


class PoidsHebdomadaireForm(BootstrapFormMixin, forms.ModelForm):
    date = champ_date(label="Date")

    class Meta:
        model = PoidsHebdomadaire
        exclude = ["exploitation"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrapper()


class PeseeIndividuelleForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = PeseeIndividuelle
        fields = ["numero_sujet", "poids_grammes"]
        widgets = {
            # Numéro auto-incrémenté en JS selon la position de la ligne :
            # le champ reste soumis (readonly, pas disabled) mais non modifiable à la main.
            "numero_sujet": forms.NumberInput(attrs={"readonly": "readonly", "class": "form-control text-center bg-light numero-sujet-auto"}),
            "poids_grammes": forms.NumberInput(attrs={"step": "0.01", "placeholder": "Poids en g"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrapper()


# Permet de saisir plusieurs pesées individuelles (10 % du cheptel) sur la
# même page que la semaine de pesée, comme sur la fiche papier.
PeseeIndividuelleFormSet = inlineformset_factory(
    PoidsHebdomadaire,
    PeseeIndividuelle,
    form=PeseeIndividuelleForm,
    extra=6,
    can_delete=True,
)


class PeseeQuotidienneOeufsForm(BootstrapFormMixin, forms.ModelForm):
    date = champ_date(label="Date")
    heure_pesee = champ_heure(label="Heure de pesée")

    class Meta:
        model = PeseeQuotidienneOeufs
        exclude = ["exploitation"]
        widgets = {
            "observations": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrapper()


class RapportJournalierForm(BootstrapFormMixin, forms.ModelForm):
    date = champ_date(label="Date")

    class Meta:
        model = RapportJournalier
        # exploitation et effectif_restant sont gérés automatiquement (jamais dans le formulaire).
        exclude = ["exploitation", "effectif_restant", "cree_le"]
        widgets = {
            "protocole_traitement_vaccination": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrapper()
