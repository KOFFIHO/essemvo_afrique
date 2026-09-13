"""
Filtres pour les templates d'impression/PDF.

`image_base64` convertit un ImageField en data-URI base64 : cela évite tout
problème de résolution de chemin/URL par xhtml2pdf (le cas qui posait
problème : logo et étiquettes de vaccin absents du PDF téléchargé, surtout
une fois l'application déployée). L'image est directement embarquée dans
le HTML, donc toujours disponible quel que soit l'hébergement.
"""

import base64

from django import template

register = template.Library()

EXTENSIONS_MIME = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "webp": "image/webp",
    "bmp": "image/bmp",
}


@register.filter
def image_base64(champ_fichier):
    """Retourne une data-URI base64 pour un ImageField, ou une chaîne vide si indisponible."""
    if not champ_fichier:
        return ""
    try:
        champ_fichier.open("rb")
        try:
            contenu = champ_fichier.read()
        finally:
            champ_fichier.close()
    except Exception:
        return ""

    nom = getattr(champ_fichier, "name", "") or ""
    extension = nom.rsplit(".", 1)[-1].lower() if "." in nom else "png"
    mime = EXTENSIONS_MIME.get(extension, "image/png")

    encode = base64.b64encode(contenu).decode("ascii")
    return f"data:{mime};base64,{encode}"
