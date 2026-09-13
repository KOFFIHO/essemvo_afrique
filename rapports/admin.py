from django.contrib import admin

from .models import (
    AppareilConnecte,
    CompteGoogleDrive,
    Exploitation,
    FicheVaccinationEauBoisson,
    FicheVaccinationInjection,
    ImageEtiquetteVaccinEau,
    PeseeIndividuelle,
    PeseeQuotidienneOeufs,
    PoidsHebdomadaire,
    RapportJournalier,
)


@admin.register(Exploitation)
class ExploitationAdmin(admin.ModelAdmin):
    list_display = ("nom", "proprietaire", "localisation", "effectif_initial", "date_creation")
    search_fields = ("nom", "localisation")


class ImageEtiquetteVaccinEauInline(admin.TabularInline):
    model = ImageEtiquetteVaccinEau
    extra = 1


@admin.register(FicheVaccinationEauBoisson)
class FicheVaccinationEauBoissonAdmin(admin.ModelAdmin):
    list_display = (
        "numero_fiche", "exploitation", "date", "vaccin_utilise",
        "nombre_sujets", "date_validite_vaccin",
    )
    list_filter = ("exploitation", "type_eau_utilisee", "date")
    search_fields = ("vaccin_utilise",)
    inlines = [ImageEtiquetteVaccinEauInline]


@admin.register(FicheVaccinationInjection)
class FicheVaccinationInjectionAdmin(admin.ModelAdmin):
    list_display = (
        "numero_fiche", "exploitation", "date", "produit_complementaire",
        "nombre_sujets", "date_validite_vaccin",
    )
    list_filter = ("exploitation", "date")


class PeseeIndividuelleInline(admin.TabularInline):
    model = PeseeIndividuelle
    extra = 5


@admin.register(PoidsHebdomadaire)
class PoidsHebdomadaireAdmin(admin.ModelAdmin):
    list_display = ("semaine_numero", "exploitation", "date", "aliment_utilise", "poids_moyen_vise")
    list_filter = ("exploitation",)
    inlines = [PeseeIndividuelleInline]


@admin.register(PeseeQuotidienneOeufs)
class PeseeQuotidienneOeufsAdmin(admin.ModelAdmin):
    list_display = (
        "date", "exploitation", "nombre_oeufs_peses",
        "poids_total_grammes", "poids_moyen_oeuf",
    )
    list_filter = ("exploitation",)


@admin.register(CompteGoogleDrive)
class CompteGoogleDriveAdmin(admin.ModelAdmin):
    list_display = ("utilisateur", "connecte_le")
    readonly_fields = ("jeton_acces", "jeton_rafraichissement", "connecte_le")


@admin.register(AppareilConnecte)
class AppareilConnecteAdmin(admin.ModelAdmin):
    list_display = ("utilisateur", "agent_utilisateur", "adresse_ip", "connecte_le", "derniere_activite")
    list_filter = ("utilisateur",)
    readonly_fields = ("cle_session", "connecte_le", "derniere_activite")


@admin.register(RapportJournalier)
class RapportJournalierAdmin(admin.ModelAdmin):
    list_display = (
        "date", "exploitation", "age_jour", "effectif_depart",
        "mortalite_jour", "effectif_restant",
    )
    list_filter = ("exploitation",)
    readonly_fields = ("effectif_restant",)
