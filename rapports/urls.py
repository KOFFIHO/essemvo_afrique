from django.urls import path

from . import views

urlpatterns = [
    path("", views.accueil, name="accueil"),

    # Exploitations
    path("exploitations/", views.liste_exploitations, name="exploitation_list"),
    path("exploitations/nouvelle/", views.creer_exploitation, name="exploitation_creer"),
    path("exploitations/<int:pk>/modifier/", views.modifier_exploitation, name="exploitation_modifier"),
    path("exploitations/<int:pk>/choisir/", views.choisir_exploitation, name="exploitation_choisir"),

    # Vaccination — eau de boisson
    path("vaccination/eau/", views.vaccination_eau_list, name="vaccination_eau_list"),
    path("vaccination/eau/nouvelle/", views.vaccination_eau_create, name="vaccination_eau_create"),
    path("vaccination/eau/<int:pk>/", views.vaccination_eau_detail, name="vaccination_eau_detail"),
    path("vaccination/eau/<int:pk>/modifier/", views.vaccination_eau_update, name="vaccination_eau_update"),
    path("vaccination/eau/<int:pk>/supprimer/", views.vaccination_eau_delete, name="vaccination_eau_delete"),

    # Vaccination — injection
    path("vaccination/injection/", views.vaccination_injection_list, name="vaccination_injection_list"),
    path("vaccination/injection/nouvelle/", views.vaccination_injection_create, name="vaccination_injection_create"),
    path("vaccination/injection/<int:pk>/", views.vaccination_injection_detail, name="vaccination_injection_detail"),
    path("vaccination/injection/<int:pk>/modifier/", views.vaccination_injection_update, name="vaccination_injection_update"),
    path("vaccination/injection/<int:pk>/supprimer/", views.vaccination_injection_delete, name="vaccination_injection_delete"),

    # Poids hebdomadaire visé
    path("poids/", views.poids_semaine_list, name="poids_semaine_list"),
    path("poids/nouvelle/", views.poids_semaine_create, name="poids_semaine_create"),
    path("poids/<int:pk>/", views.poids_semaine_detail, name="poids_semaine_detail"),
    path("poids/<int:pk>/modifier/", views.poids_semaine_update, name="poids_semaine_update"),
    path("poids/<int:pk>/supprimer/", views.poids_semaine_delete, name="poids_semaine_delete"),

    # Pesée quotidienne des œufs
    path("oeufs/", views.pesee_oeufs_list, name="pesee_oeufs_list"),
    path("oeufs/nouvelle/", views.pesee_oeufs_create, name="pesee_oeufs_create"),
    path("oeufs/<int:pk>/supprimer/", views.pesee_oeufs_delete, name="pesee_oeufs_delete"),

    # --- Impression / PDF (format A4) ---
    path("vaccination/eau/<int:pk>/imprimer/", views.vaccination_eau_imprimer, name="vaccination_eau_imprimer"),
    path("vaccination/eau/<int:pk>/pdf/", views.vaccination_eau_pdf, name="vaccination_eau_pdf"),

    path("vaccination/injection/<int:pk>/imprimer/", views.vaccination_injection_imprimer, name="vaccination_injection_imprimer"),
    path("vaccination/injection/<int:pk>/pdf/", views.vaccination_injection_pdf, name="vaccination_injection_pdf"),

    path("poids/<int:pk>/imprimer/", views.poids_semaine_imprimer, name="poids_semaine_imprimer"),
    path("poids/<int:pk>/pdf/", views.poids_semaine_pdf, name="poids_semaine_pdf"),

    path("oeufs/imprimer/", views.pesee_oeufs_imprimer, name="pesee_oeufs_imprimer"),
    path("oeufs/pdf/", views.pesee_oeufs_pdf, name="pesee_oeufs_pdf"),

    # --- Historique complet (filtré) : impression / PDF ---
    path("vaccination/eau/historique/imprimer/", views.vaccination_eau_liste_imprimer, name="vaccination_eau_liste_imprimer"),
    path("vaccination/eau/historique/pdf/", views.vaccination_eau_liste_pdf, name="vaccination_eau_liste_pdf"),

    path("vaccination/injection/historique/imprimer/", views.vaccination_injection_liste_imprimer, name="vaccination_injection_liste_imprimer"),
    path("vaccination/injection/historique/pdf/", views.vaccination_injection_liste_pdf, name="vaccination_injection_liste_pdf"),

    path("poids/historique/imprimer/", views.poids_semaine_liste_imprimer, name="poids_semaine_liste_imprimer"),
    path("poids/historique/pdf/", views.poids_semaine_liste_pdf, name="poids_semaine_liste_pdf"),
]
