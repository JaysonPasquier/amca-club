#!/bin/bash

# Script d'Installation du Site Web Club de Voitures Américaines

echo "Configuration du site Web Club de Voitures Américaines..."

# Create necessary directories
mkdir -p backend/static backend/media/profile_images
mkdir -p frontend/src/{components,pages,services,assets}

# Backend setup
cd backend
echo "Configuration du backend..."
python3 -m venv venv
source venv/bin/activate || { echo "Impossible d'activer l'environnement virtuel. Utilisez: python3 -m venv venv && source venv/bin/activate"; exit 1; }
pip install -r requirements.txt

# Create default profile image
touch media/profile_images/default.png

# Create database and run migrations
echo "Configuration de la base de données... (assurez-vous que PostgreSQL est installé et en cours d'exécution)"
echo "Si l'erreur 'role \"scorpio\" does not exist' apparaît, exécutez: sudo -u postgres createuser -s scorpio"
createdb amca_db || echo "La base de données existe peut-être déjà"
python manage.py makemigrations accounts core
python manage.py migrate

# Create initial data
python manage.py shell -c "
from core.models import ClubInfo;
if not ClubInfo.objects.exists():
    ClubInfo.objects.create(
        name='Club de Voitures Américaines',
        description='Une communauté pour les amateurs de voitures américaines.',
        founder_info='Notre fondateur est passionné par les voitures américaines depuis son enfance.',
        cofounder_info='Notre co-fondateur apporte 15 ans d'expérience dans la restauration automobile.'
    )
    print('Informations du club créées !')
"

echo "Voulez-vous créer un superutilisateur ? (o/n)"
read create_superuser
if [ "$create_superuser" = "o" ]; then
    python manage.py createsuperuser
fi

cd ../frontend
echo "Configuration du frontend..."
npm init -y
npm install react react-dom react-router-dom axios bootstrap @fortawesome/fontawesome-free

echo "Configuration terminée !"
echo "Pour exécuter le serveur backend : cd backend && source venv/bin/activate && python manage.py runserver"
echo "Pour exécuter le serveur frontend (après implémentation de l'application React) : cd frontend && npm start"
