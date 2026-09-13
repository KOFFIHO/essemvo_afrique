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
    date_arrivee_sujets = models.DateTimeField(
        "Date et heure d'arrivée des sujets", null=True, blank=True,
        help_text="Sert à calculer automatiquement l'âge des sujets (en jours) sur toutes les fiches.",
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Exploitation"
        verbose_name_plural = "Exploitations"
        ordering = ["nom"]

    def __str__(self):
        return self.nom

    @property
    def dimensions_logo_pdf(self):
        """
        Calcule (largeur, hauteur) en pixels pour le logo dans l'en-tête PDF,
        en conservant strictement les proportions d'origine du fichier
        (xhtml2pdf déforme parfois une image si seule la hauteur CSS est
        précisée : on fixe donc explicitement largeur ET hauteur, calculées
        depuis les dimensions réelles).
        """
        if not self.logo:
            return None
        try:
            from PIL import Image as ImagePIL

            with self.logo.open("rb") as fichier:
                image = ImagePIL.open(fichier)
                largeur_orig, hauteur_orig = image.size
        except Exception:
            return None

        if not largeur_orig or not hauteur_orig:
            return None

        hauteur_max, largeur_max = 42, 130
        ratio = min(hauteur_max / hauteur_orig, largeur_max / largeur_orig, 1)
        return {
            "largeur": max(1, round(largeur_orig * ratio)),
            "hauteur": max(1, round(hauteur_orig * ratio)),
        }


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
    def age_sujets(self):
        """Âge des sujets (en jours), calculé automatiquement depuis la date d'arrivée de l'exploitation."""
        if not self.exploitation.date_arrivee_sujets:
            return None
        return (self.date - self.exploitation.date_arrivee_sujets.date()).days + 1

    @property
    def quantite_eau_consommee(self):
        return self.quantite_eau_initiale - self.quantite_eau_reste


class ImageEtiquetteVaccinEau(models.Model):
    """Une photo d'étiquette de vaccin liée à une fiche eau de boisson (plusieurs possibles par fiche)."""

    fiche = models.ForeignKey(
        FicheVaccinationEauBoisson, on_delete=models.CASCADE, related_name="images_etiquettes"
    )
    image = models.ImageField("Image étiquette du vaccin", upload_to="etiquettes_vaccin_eau/")
    televerse_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Image étiquette (eau de boisson)"
        verbose_name_plural = "Images étiquettes (eau de boisson)"
        ordering = ["televerse_le"]

    def __str__(self):
        return f"Image étiquette — fiche n°{self.fiche.numero_fiche}"


class FicheVaccinationInjection(models.Model):
    """FICHE DE RAPPORT DE VACCINATION ~ Injection."""

    exploitation = models.ForeignKey(
        Exploitation, on_delete=models.CASCADE, related_name="fiches_vaccination_injection"
    )
    numero_fiche = models.PositiveIntegerField("N° de la fiche")
    date = models.DateField("Date")
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

    @property
    def age_sujets(self):
        """Âge des sujets (en jours), calculé automatiquement depuis la date d'arrivée de l'exploitation."""
        if not self.exploitation.date_arrivee_sujets:
            return None
        return (self.date - self.exploitation.date_arrivee_sujets.date()).days + 1


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


class AppareilConnecte(models.Model):
    """
    Un appareil (session) actuellement connecté à un compte utilisateur.
    Utilisé pour limiter le nombre de connexions simultanées par compte.
    """

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="appareils_connectes"
    )
    cle_session = models.CharField("Clé de session", max_length=40, unique=True)
    agent_utilisateur = models.CharField("Appareil / navigateur", max_length=255, blank=True)
    adresse_ip = models.GenericIPAddressField("Adresse IP", null=True, blank=True)
    connecte_le = models.DateTimeField("Connecté depuis", auto_now_add=True)
    derniere_activite = models.DateTimeField("Dernière activité", auto_now=True)

    class Meta:
        verbose_name = "Appareil connecté"
        verbose_name_plural = "Appareils connectés"
        ordering = ["-derniere_activite"]

    def __str__(self):
        return f"{self.utilisateur} — {self.agent_utilisateur or 'appareil inconnu'}"


class CompteGoogleDrive(models.Model):
    """Jetons OAuth2 permettant d'envoyer des fiches PDF vers le Google Drive de l'utilisateur."""

    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="compte_drive"
    )
    jeton_acces = models.TextField("Jeton d'accès")
    jeton_rafraichissement = models.TextField("Jeton de rafraîchissement", blank=True)
    connecte_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Compte Google Drive"
        verbose_name_plural = "Comptes Google Drive"

    def __str__(self):
        return f"Google Drive de {self.utilisateur}"


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


class RapportJournalier(models.Model):
    """
    FICHE DES RAPPORTS JOURNALIERS POUR LES POULES PONDEUSES.
    Un enregistrement par jour et par exploitation.
    """

    exploitation = models.ForeignKey(
        Exploitation, on_delete=models.CASCADE, related_name="rapports_journaliers"
    )
    date = models.DateField("Date")

    mortalite_jour = models.PositiveIntegerField("Mortalité de la journée", default=0)
    # Calculé automatiquement à l'enregistrement (voir save()) — jamais saisi à la main.
    effectif_restant = models.PositiveIntegerField("Effectif restant", editable=False, default=0)

    conso_aliments_kg = models.DecimalField(
        "Consommation en aliments (kg)", max_digits=7, decimal_places=2, null=True, blank=True
    )
    conso_eau_litres = models.DecimalField(
        "Consommation en eau (L)", max_digits=7, decimal_places=2, null=True, blank=True
    )
    production_oeufs_plaquettes = models.DecimalField(
        "Production d'œufs (plaquettes)", max_digits=6, decimal_places=1, null=True, blank=True
    )
    nombre_oeufs_casses = models.PositiveIntegerField("Nombre d'œufs cassés", null=True, blank=True)
    poids_moyen_oeufs = models.DecimalField(
        "Poids moyen des œufs (g)", max_digits=6, decimal_places=2, null=True, blank=True
    )
    protocole_traitement_vaccination = models.TextField(
        "Protocoles de traitement et de vaccination", blank=True
    )

    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Rapport journalier"
        verbose_name_plural = "Rapports journaliers"
        ordering = ["-date"]
        unique_together = ("exploitation", "date")

    def __str__(self):
        return f"Rapport du {self.date} — {self.exploitation}"

    def get_absolute_url(self):
        return reverse("rapport_journalier_detail", args=[self.pk])

    @property
    def age_jour(self):
        """Âge en jours, calculé depuis la date d'arrivée des sujets de l'exploitation."""
        if not self.exploitation.date_arrivee_sujets:
            return None
        return (self.date - self.exploitation.date_arrivee_sujets.date()).days + 1

    @property
    def effectif_depart(self):
        """Effectif de départ : celui de l'exploitation, identique sur toute la durée du lot."""
        return self.exploitation.effectif_initial

    def _calculer_effectif_restant(self):
        precedent = (
            RapportJournalier.objects.filter(exploitation=self.exploitation, date__lt=self.date)
            .exclude(pk=self.pk)
            .order_by("-date")
            .first()
        )
        base = precedent.effectif_restant if precedent else self.exploitation.effectif_initial
        return max(0, base - self.mortalite_jour)

    def save(self, *args, **kwargs):
        self.effectif_restant = self._calculer_effectif_restant()
        super().save(*args, **kwargs)

        # Recalcule en cascade les jours suivants (utile si on modifie
        # la mortalité d'un jour déjà passé : tous les jours après doivent
        # être recalculés à partir du nouvel effectif restant).
        base = self.effectif_restant
        for suivant in RapportJournalier.objects.filter(
            exploitation=self.exploitation, date__gt=self.date
        ).order_by("date"):
            nouveau = max(0, base - suivant.mortalite_jour)
            if nouveau != suivant.effectif_restant:
                RapportJournalier.objects.filter(pk=suivant.pk).update(effectif_restant=nouveau)
            base = nouveau
