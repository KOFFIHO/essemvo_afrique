# 🌿 ARGILE — La Mémoire du Fermier

Plateforme web de rapports d'élevage avicole (poules pondeuses), développée
avec **Django** (backend) et **HTML / CSS / Bootstrap 5** (frontend),
thème vert nature.

Reprend numériquement les fiches papier :
- **Fiche de rapport de vaccination en eau de boisson**
- **Fiche de rapport de vaccination — Injection**
- **Poids moyen hebdomadaire visé** (pesée de 10 % du cheptel)
- **Pesée quotidienne des œufs**

## 1. Installation

```bash
python -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configuration de la base de données

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## 3. Lancer le serveur

```bash
python manage.py runserver
```

Ouvrez ensuite http://127.0.0.1:8000/connexion/

## 4. Premiers pas

1. Connectez-vous avec le compte créé (`createsuperuser`).
2. Créez votre **exploitation** (menu "Exploitations").
3. Commencez à saisir vos fiches depuis le tableau de bord.
4. L'espace `/admin/` reste disponible pour une gestion avancée.

## 5. Arborescence

```
argile_project/
├── manage.py
├── requirements.txt
├── config/                # réglages, urls, wsgi/asgi
├── rapports/               # app métier (modèles, vues, formulaires, admin)
│   └── migrations/
├── templates/
│   ├── rapports/           # tableau de bord + fiches
│   └── registration/       # page de connexion
└── static/
    └── css/argile.css      # thème vert nature
```

## 6. Personnalisation visuelle

Les couleurs du thème sont centralisées en haut du fichier
`static/css/argile.css` (variables CSS `--argile-vert`, `--argile-terre`,
`--argile-jaune-oeuf`, etc.) — modifiez-les pour ajuster la charte.

---
Inspiré de « La Mémoire du Fermier — Poules Pondeuses » (ESSEMVO AFRIQUE).
