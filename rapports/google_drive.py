"""
Intégration Google Drive pour ARGILE.

Permet à chaque utilisateur de connecter son propre compte Google Drive
(OAuth2) et d'y envoyer les fiches PDF générées, rangées automatiquement
dans une arborescence de dossiers :

    ARGILE / <Nom de l'exploitation> / <Type de fiche> / fichier.pdf

Prérequis côté Google Cloud Console (à faire une seule fois, voir le
README) : créer un projet, activer l'API "Google Drive API", créer un
identifiant OAuth 2.0 de type "Application Web", puis renseigner les
variables GOOGLE_OAUTH_CLIENT_ID / GOOGLE_OAUTH_CLIENT_SECRET (voir
config/settings.py).
"""

import io
import os

from django.conf import settings
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# En développement (HTTP, sans certificat SSL), la bibliothèque OAuth
# refuse par défaut les échanges non chiffrés. On l'autorise uniquement
# quand DEBUG est actif (jamais en production).
if settings.DEBUG:
    os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
DOSSIER_RACINE = "ARGILE"


def construire_flow(state=None):
    """Construit le "Flow" OAuth2 utilisé pour la connexion et le callback."""
    configuration_client = {
        "web": {
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [settings.GOOGLE_OAUTH_REDIRECT_URI],
        }
    }
    return Flow.from_client_config(
        configuration_client,
        scopes=SCOPES,
        state=state,
        redirect_uri=settings.GOOGLE_OAUTH_REDIRECT_URI,
    )


def credentials_depuis_compte(compte):
    """Reconstruit des Credentials Google à partir des jetons stockés en base,
    et les rafraîchit automatiquement si nécessaire (le nouveau jeton est
    aussitôt sauvegardé)."""
    creds = Credentials(
        token=compte.jeton_acces,
        refresh_token=compte.jeton_rafraichissement or None,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
        client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
        scopes=SCOPES,
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        compte.jeton_acces = creds.token
        compte.save(update_fields=["jeton_acces"])
    return creds


def _trouver_ou_creer_dossier(service, nom, parent_id=None):
    """Cherche un dossier par nom (sous `parent_id` si fourni) et le crée s'il n'existe pas."""
    nom_echappe = nom.replace("'", "\\'")
    requete = (
        f"name = '{nom_echappe}' and mimeType = 'application/vnd.google-apps.folder' "
        "and trashed = false"
    )
    if parent_id:
        requete += f" and '{parent_id}' in parents"

    resultats = service.files().list(q=requete, spaces="drive", fields="files(id, name)").execute()
    fichiers = resultats.get("files", [])
    if fichiers:
        return fichiers[0]["id"]

    metadonnees = {"name": nom, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        metadonnees["parents"] = [parent_id]
    dossier = service.files().create(body=metadonnees, fields="id").execute()
    return dossier["id"]


def televerser_pdf(compte, nom_exploitation, type_fiche, nom_fichier, contenu_pdf):
    """
    Envoie le PDF dans Drive/ARGILE/<exploitation>/<type de fiche>/<nom_fichier>,
    en créant les dossiers manquants. Retourne le lien Drive du fichier créé.
    """
    creds = credentials_depuis_compte(compte)
    service = build("drive", "v3", credentials=creds)

    id_racine = _trouver_ou_creer_dossier(service, DOSSIER_RACINE)
    id_exploitation = _trouver_ou_creer_dossier(service, nom_exploitation, id_racine)
    id_type = _trouver_ou_creer_dossier(service, type_fiche, id_exploitation)

    media = MediaIoBaseUpload(io.BytesIO(contenu_pdf), mimetype="application/pdf", resumable=False)
    metadonnees = {"name": nom_fichier, "parents": [id_type]}
    fichier = (
        service.files()
        .create(body=metadonnees, media_body=media, fields="id, webViewLink")
        .execute()
    )
    return fichier.get("webViewLink")
