# Club de Voitures Américaines - Site Web

Site web officiel du Club de Voitures Américaines. Cette application permet la gestion des membres, des événements et fournit des informations sur le club.

## Fonctionnalités

- Système d'adhésion avec approbation administrateur
- Profils de membres personnalisables
- Gestion d'événements
- Newsletter
- Interface administrateur pour la gestion de contenu

## Installation

1. Cloner le dépôt:
   ```bash
   git clone https://github.com/votre-username/amca-club.git
   cd amca-club
   ```

2. Installer les dépendances:
   ```bash
   cd v1/backend
   python -m venv venv
   source venv/bin/activate  # Sur Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configuration de la base de données:
   ```bash
   python manage.py migrate
   ```

4. Créer un superutilisateur:
   ```bash
   python manage.py createsuperuser
   ```

5. Lancer le serveur:
   ```bash
   python manage.py runserver
   ```

## Structure du projet

- `/v1/backend/` - Application Django principale
  - `/accounts/` - Gestion des utilisateurs et profils
  - `/core/` - Fonctionnalités principales (événements, infos club)
  - `/api/` - API REST pour communication avec le frontend

## Notes de développement

- Django 4.2.7
- Base de données: SQLite en développement, PostgreSQL recommandé en production
- Interface administrateur disponible à /admin/

## Maintenance

Pour mettre à jour le site:
1. Pull les dernières modifications
2. Appliquer les migrations si nécessaire
3. Redémarrer le serveur
