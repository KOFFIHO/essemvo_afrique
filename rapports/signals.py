"""
Limite le nombre d'appareils simultanément connectés à un même compte
utilisateur. Au-delà de LIMITE_APPAREILS, la session la plus ancienne est
automatiquement invalidée (déconnexion forcée de cet appareil).
"""

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.sessions.models import Session
from django.dispatch import receiver
from django.utils import timezone

from .models import AppareilConnecte

LIMITE_APPAREILS = 5


def _agent_utilisateur(request):
    return request.META.get("HTTP_USER_AGENT", "")[:255]


def _adresse_ip(request):
    return request.META.get("REMOTE_ADDR")


@receiver(user_logged_in)
def enregistrer_appareil_et_limiter(sender, request, user, **kwargs):
    cle_session = request.session.session_key
    if not cle_session:
        # Force la création de la session si elle n'existe pas encore.
        request.session.save()
        cle_session = request.session.session_key

    AppareilConnecte.objects.update_or_create(
        cle_session=cle_session,
        defaults={
            "utilisateur": user,
            "agent_utilisateur": _agent_utilisateur(request),
            "adresse_ip": _adresse_ip(request),
        },
    )

    # Ne conserver que les appareils dont la session Django est encore valide.
    appareils = list(
        AppareilConnecte.objects.filter(utilisateur=user).order_by("connecte_le")
    )
    cles_valides = set(
        Session.objects.filter(expire_date__gt=timezone.now()).values_list("session_key", flat=True)
    )
    appareils_valides = [a for a in appareils if a.cle_session in cles_valides]

    # Nettoie les enregistrements devenus obsolètes (session expirée depuis longtemps).
    ids_valides = {a.id for a in appareils_valides}
    AppareilConnecte.objects.filter(utilisateur=user).exclude(id__in=ids_valides).delete()

    if len(appareils_valides) > LIMITE_APPAREILS:
        excedent = appareils_valides[: len(appareils_valides) - LIMITE_APPAREILS]
        for appareil in excedent:
            Session.objects.filter(session_key=appareil.cle_session).delete()
            appareil.delete()


@receiver(user_logged_out)
def retirer_appareil(sender, request, user, **kwargs):
    if request.session.session_key:
        AppareilConnecte.objects.filter(cle_session=request.session.session_key).delete()
