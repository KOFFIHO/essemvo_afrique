"""
Modèles ARGILE — reprennent les fiches papier « La Mémoire du Fermier »
(ESSEMVO Afrique) : vaccination en eau de boisson, vaccination par
injection, poids moyen hebdomadaire visé, et pesée quotidienne des œufs.
"""

from django.conf import settings
from django.db import models
from django.urls import reverse


class Exploitation(models.Model):
    """Le poulailler / la ferme suivie par l'utilisateur."""

    nom = models.CharField("Nom de l'exploitation", max_length=150)
    logo = models.ImageField("Logo de la ferme", upload_to="logos_exploitations/", blank=True, null=True)
    proprietaire = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="exploitations"
    )
    localisation = models.CharField("Localisation", max_length=150, blank=True)
    effectif_initial = models.PositiveIntegerField("Effectif initial (sujets)", default=0)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Exploitation"
        verbose_name_plural = "Exploitations"
        ordering = ["nom"]

    def __str__(self):
        return self.nom


class TypeEauChoices(models.TextChoices):
    PUITS = "PUITS", "Puits"
    FORAGE = "FORAGE", "Forage"


class FicheVaccinationEauBoisson(models.Model):
    """FICHE DE RAPPORT DE VACCINATION EN EAU DE BOISSON."""

    exploitation = models.ForeignKey(
        Exploitation, on_delete=models.CASCADE, related_name="fiches_vaccination_eau"
    )
    numero_fiche = models.PositiveIntegerField("N° de la fiche")
    date = models.DateField("Date")
    age_sujets = models.CharField("Âge des sujets", max_length=50)
    nombre_sujets = models.PositiveIntegerField("Nombre de sujets")
    nombre_doses_utilise = models.PositiveIntegerField("Nombre de doses utilisées")

    vaccin_utilise = models.CharField("Vaccin utilisé (nom)", max_length=150)
    type_eau_utilisee = models.CharField(
        "Type d'eau utilisée", max_length=10, choices=TypeEauChoices.choices
    )
    quantite_eau_initiale = models.DecimalField(
        "Quantité d'eau initiale (L)", max_digits=6, decimal_places=2
    )
    quantite_eau_reste = models.DecimalField(
        "Quantité d'eau restante (L)", max_digits=6, decimal_places=2, default=0
    )

    heure_assoiffement_debut = models.TimeField("Heure d'assoiffement — début")
    heure_assoiffement_fin = models.TimeField("Heure d'assoiffement — fin")
    heure_abreuvement_debut = models.TimeField("Heure d'abreuvement — début")
    heure_abreuvement_fin = models.TimeField("Heure d'abreuvement — fin")

    date_validite_vaccin = models.DateField("Date de validité du vaccin")
    image_etiquette = models.ImageField(
        "Image étiquette du vaccin", upload_to="etiquettes_vaccin_eau/", blank=True, null=True
    )
    observations = models.TextField("Observations", blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Fiche vaccination — eau de boisson"
        verbose_name_plural = "Fiches vaccination — eau de boisson"
        ordering = ["-date", "-numero_fiche"]

    def __str__(self):
        return f"Fiche eau de boisson n°{self.numero_fiche} — {self.date}"

    def get_absolute_url(self):
        return reverse("vaccination_eau_detail", args=[self.pk])

    @property
    def quantite_eau_consommee(self):
        return self.quantite_eau_initiale - self.quantite_eau_reste


class FicheVaccinationInjection(models.Model):
    """FICHE DE RAPPORT DE VACCINATION ~ Injection."""

    exploitation = models.ForeignKey(
        Exploitation, on_delete=models.CASCADE, related_name="fiches_vaccination_injection"
    )
    numero_fiche = models.PositiveIntegerField("N° de la fiche")
    date = models.DateField("Date")
    age_sujets = models.CharField("Âge des sujets", max_length=50)
    nombre_sujets = models.PositiveIntegerField("Nombre de sujets")
    nombre_doses_utilise = models.PositiveIntegerField("Nombre de doses utilisées")

    quantite_produit_ml = models.DecimalField(
        "Quantité du produit (ml)", max_digits=7, decimal_places=2, default=0
    )
    nom_vaccin = models.CharField("Nom du vaccin", max_length=150, blank=True)
    produit_complementaire = models.CharField(
        "Produit complémentaire utilisé", max_length=150, blank=True
    )
    image_etiquette = models.ImageField(
        "Image étiquette du vaccin", upload_to="etiquettes_vaccin_injection/", blank=True, null=True
    )

    heure_debut = models.TimeField("Heure de début (injection)")
    heure_fin = models.TimeField("Heure de fin (injection)")

    date_validite_vaccin = models.DateField("Date de validité du vaccin")
    observations = models.TextField("Observations", blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Fiche vaccination — injection"
        verbose_name_plural = "Fiches vaccination — injection"
        ordering = ["-date", "-numero_fiche"]

    def __str__(self):
        return f"Fiche injection n°{self.numero_fiche} — {self.date}"

    def get_absolute_url(self):
        return reverse("vaccination_injection_detail", args=[self.pk])


class PoidsHebdomadaire(models.Model):
    """POIDS MOYEN HEBDOMADAIRE VISE — en-tête d'une semaine de pesée."""

    exploitation = models.ForeignKey(
        Exploitation, on_delete=models.CASCADE, related_name="semaines_poids"
    )
    semaine_numero = models.PositiveIntegerField("Semaine n°")
    date = models.DateField("Date")
    aliment_utilise = models.CharField("Aliment utilisé pour l'alimentation", max_length=150)
    poids_moyen_vise = models.DecimalField(
        "Poids moyen hebdomadaire visé (g)", max_digits=7, decimal_places=2
    )
    fourchette_min = models.DecimalField(
        "Fourchette de poids — minimum (g)", max_digits=7, decimal_places=2, null=True, blank=True
    )
    fourchette_max = models.DecimalField(
        "Fourchette de poids — maximum (g)", max_digits=7, decimal_places=2, null=True, blank=True
    )

    class Meta:
        verbose_name = "Semaine de pesée"
        verbose_name_plural = "Semaines de pesée"
        ordering = ["exploitation", "semaine_numero"]
        unique_together = ("exploitation", "semaine_numero")

    def __str__(self):
        return f"Semaine n°{self.semaine_numero} ({self.exploitation})"

    def get_absolute_url(self):
        return reverse("poids_semaine_detail", args=[self.pk])

    @property
    def nombre_poussins_peses(self):
        return self.pesees.count()

    @property
    def poids_total(self):
        return sum((p.poids_grammes for p in self.pesees.all()), 0)

    @property
    def poids_moyen_reel(self):
        n = self.nombre_poussins_peses
        if n == 0:
            return None
        return round(self.poids_total / n, 2)

    @property
    def fourchette_affichage(self):
        if self.fourchette_min is not None and self.fourchette_max is not None:
            return f"{self.fourchette_min} – {self.fourchette_max} g"
        return None


class PeseeIndividuelle(models.Model):
    """Une case du tableau « POIDS » (10 % du cheptel pesé chaque semaine)."""

    semaine = models.ForeignKey(
        PoidsHebdomadaire, on_delete=models.CASCADE, related_name="pesees"
    )
    numero_sujet = models.PositiveIntegerField("N° du sujet pesé")
    poids_grammes = models.DecimalField("Poids (g)", max_digits=7, decimal_places=2)

    class Meta:
        verbose_name = "Pesée individuelle"
        verbose_name_plural = "Pesées individuelles"
        ordering = ["numero_sujet"]
        unique_together = ("semaine", "numero_sujet")

    def __str__(self):
        return f"Sujet {self.numero_sujet} : {self.poids_grammes} g"


class PeseeQuotidienneOeufs(models.Model):
    """Pesée quotidienne des œufs (suivi de la performance pondérale)."""

    exploitation = models.ForeignKey(
        Exploitation, on_delete=models.CASCADE, related_name="pesees_oeufs"
    )
    date = models.DateField("Date")
    heure_pesee = models.TimeField("Heure de pesée", default="17:00")
    nombre_oeufs_peses = models.PositiveIntegerField("Nombre d'œufs pesés (échantillon)")
    poids_total_grammes = models.DecimalField("Poids total (g)", max_digits=8, decimal_places=2)
    observations = models.TextField("Observations", blank=True)

    class Meta:
        verbose_name = "Pesée quotidienne des œufs"
        verbose_name_plural = "Pesées quotidiennes des œufs"
        ordering = ["-date"]
        unique_together = ("exploitation", "date")

    def __str__(self):
        return f"Pesée œufs du {self.date}"

    def get_absolute_url(self):
        return reverse("pesee_oeufs_list")

    @property
    def poids_moyen_oeuf(self):
        if not self.nombre_oeufs_peses:
            return None
        return round(self.poids_total_grammes / self.nombre_oeufs_peses, 2)
