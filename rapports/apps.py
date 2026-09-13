from django.apps import AppConfig


class RapportsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rapports"
    verbose_name = "Rapports d'élevage"

    def ready(self):
        from . import signals  # noqa: F401 — connecte les signaux (limite d'appareils)
