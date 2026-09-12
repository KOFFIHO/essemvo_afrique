from django.contrib import admin

from .models import (
    Exploitation,
    FicheVaccinationEauBoisson,
    FicheVaccinationInjection,
    PeseeIndividuelle,
    PeseeQuotidienneOeufs,
    PoidsHebdomadaire,
)


@admin.register(Exploitation)
class ExploitationAdmin(admin.ModelAdmin):
    list_display = ("nom", "proprietaire", "localisation", "effectif_initial", "date_creation")
    search_fields = ("nom", "localisation")


@admin.register(FicheVaccinationEauBoisson)
class FicheVaccinationEauBoissonAdmin(admin.ModelAdmin):
    list_display = (
        "numero_fiche", "exploitation", "date", "vaccin_utilise",
        "nombre_sujets", "date_validite_vaccin",
    )
    list_filter = ("exploitation", "type_eau_utilisee", "date")
    search_fields = ("vaccin_utilise",)


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
