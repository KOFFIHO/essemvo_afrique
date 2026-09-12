"""
Rend l'exploitation actuellement sélectionnée disponible dans TOUS les
templates (notamment la navbar), sans avoir à la repasser dans chaque vue.
"""


def exploitation_courante(request):
    if not request.user.is_authenticated:
        return {}

    # Import différé pour éviter tout import circulaire avec views.py
    from .views import get_exploitation_courante

    return {"exploitation_courante": get_exploitation_courante(request)}
