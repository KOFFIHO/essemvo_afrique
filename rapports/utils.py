"""
Utilitaire de rendu PDF pour ARGILE.

Convertit un template Django (HTML + CSS simple, format A4) en fichier PDF
téléchargeable, avec la bibliothèque pure Python xhtml2pdf (pisa).
"""

import io
import os

from django.conf import settings
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


def _lien_vers_fichier(uri, rel):
    """
    Convertit une URL /static/... ou /media/... en chemin de fichier réel
    sur le disque, pour que xhtml2pdf puisse intégrer les images
    (ex. photo de l'étiquette du vaccin, logo de la ferme) dans le PDF généré.
    Fonctionne que MEDIA_URL/STATIC_URL commencent ou non par un "/".
    """
    media_url = settings.MEDIA_URL.lstrip("/")
    static_url = settings.STATIC_URL.lstrip("/")
    uri_normalise = uri.lstrip("/")

    if uri_normalise.startswith(media_url):
        sous_chemin = uri_normalise[len(media_url):]
        chemin = os.path.join(str(settings.MEDIA_ROOT), sous_chemin)
    elif uri_normalise.startswith(static_url):
        sous_chemin = uri_normalise[len(static_url):]
        chemin = finders.find(sous_chemin) or os.path.join(str(settings.STATIC_ROOT or ""), sous_chemin)
    else:
        # URL absolue (http/https) ou déjà un chemin disque : on la laisse telle quelle.
        return uri

    if not chemin or not os.path.isfile(chemin):
        # Fichier introuvable : on n'échoue pas tout le PDF pour autant.
        return uri
    return chemin


def render_to_pdf(template_src, context_dict, nom_fichier="fiche.pdf", telecharger=True):
    """
    Rend `template_src` avec `context_dict` puis retourne une HttpResponse
    contenant le PDF généré. Si `telecharger` est True, le PDF est proposé
    en téléchargement (Content-Disposition: attachment), sinon il s'ouvre
    directement dans le navigateur (utile pour un aperçu avant impression).
    """
    template = get_template(template_src)
    html = template.render(context_dict)

    resultat = io.BytesIO()
    pdf = pisa.pisaDocument(
        io.BytesIO(html.encode("UTF-8")),
        resultat,
        encoding="UTF-8",
        link_callback=_lien_vers_fichier,
    )

    if pdf.err:
        return HttpResponse("Erreur lors de la génération du PDF.", status=500)

    reponse = HttpResponse(resultat.getvalue(), content_type="application/pdf")
    disposition = "attachment" if telecharger else "inline"
    reponse["Content-Disposition"] = f'{disposition}; filename="{nom_fichier}"'
    return reponse
