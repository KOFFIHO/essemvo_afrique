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
    class Meta:
        model = Exploitation
        fields = ["nom", "logo", "localisation", "effectif_initial", "date_arrivee_sujets"]
        widgets = {
            "logo": forms.ClearableFileInput(attrs={"accept": "image/*"}),
            "date_arrivee_sujets": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrapper()


class FicheVaccinationEauBoissonForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = FicheVaccinationEauBoisson
        # numero_fiche est calculé automatiquement (voir la vue de création) : jamais dans le formulaire.
        # Les images d'étiquette sont gérées séparément (upload multiple, voir la vue).
        exclude = ["exploitation", "cree_le", "numero_fiche"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "date_validite_vaccin": forms.DateInput(attrs={"type": "date"}),
            "heure_assoiffement_debut": forms.TimeInput(attrs={"type": "time"}),
            "heure_assoiffement_fin": forms.TimeInput(attrs={"type": "time"}),
            "heure_abreuvement_debut": forms.TimeInput(attrs={"type": "time"}),
            "heure_abreuvement_fin": forms.TimeInput(attrs={"type": "time"}),
            "observations": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrapper()


class FicheVaccinationInjectionForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = FicheVaccinationInjection
        # numero_fiche est calculé automatiquement (voir la vue de création) : jamais dans le formulaire.
        exclude = ["exploitation", "cree_le", "numero_fiche"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "date_validite_vaccin": forms.DateInput(attrs={"type": "date"}),
            "heure_debut": forms.TimeInput(attrs={"type": "time"}),
            "heure_fin": forms.TimeInput(attrs={"type": "time"}),
            "observations": forms.Textarea(attrs={"rows": 3}),
            "image_etiquette": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrapper()


class PoidsHebdomadaireForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = PoidsHebdomadaire
        exclude = ["exploitation"]
        widgets = {"date": forms.DateInput(attrs={"type": "date"})}

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
    class Meta:
        model = PeseeQuotidienneOeufs
        exclude = ["exploitation"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "heure_pesee": forms.TimeInput(attrs={"type": "time"}),
            "observations": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrapper()


class RapportJournalierForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = RapportJournalier
        # exploitation et effectif_restant sont gérés automatiquement (jamais dans le formulaire).
        exclude = ["exploitation", "effectif_restant", "cree_le"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "protocole_traitement_vaccination": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrapper()
