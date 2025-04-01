# Site Web du Club de Voitures Américaines

Voici la première version du site web du Club de Voitures Américaines, avec les fonctionnalités suivantes:

- Profils des membres avec rôles et identifiants
- Système d'approbation d'administrateur pour les nouveaux comptes
- Page d'accueil avec informations sur le club
- Section événements
- Liste des membres
- Pages de profil

## Stack Technologique
- Backend: Django avec PostgreSQL
- Frontend: React
- Authentification: Authentification Django intégrée + flux d'approbation personnalisé

## Instructions d'Installation

### Configuration du Backend
1. Accédez au dossier backend: `cd backend`
2. Créez un environnement virtuel: `python -m venv venv`
3. Activez l'environnement virtuel:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Installez les dépendances: `pip install -r requirements.txt`
5. Exécutez les migrations: `python manage.py migrate`
6. Créez un superutilisateur: `python manage.py createsuperuser`
7. Démarrez le serveur: `python manage.py runserver`

### Configuration du Frontend
1. Accédez au dossier frontend: `cd frontend`
2. Installez les dépendances: `npm install`
3. Démarrez le serveur de développement: `npm start`

## Fonctionnalités
- Inscription d'utilisateur avec approbation par administrateur
- Profils de membres avec rôles
- Annuaire des membres
- Section d'événements à venir
- Abonnement à la newsletter
- Design responsive pour tous les écrans
