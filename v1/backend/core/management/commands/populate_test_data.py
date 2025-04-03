from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from django.core.files.base import ContentFile
from accounts.models import UserProfile
from core.models import Event, EventParticipant
import random
from datetime import timedelta
import os
import requests
from io import BytesIO
import hashlib

class Command(BaseCommand):
    help = 'Peuple la base de données avec des utilisateurs, événements et participants fictifs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=50,
            help='Nombre d\'utilisateurs à créer'
        )
        parser.add_argument(
            '--events',
            type=int,
            default=25,
            help='Nombre d\'événements à créer'
        )

    def handle(self, *args, **options):
        num_users = options['users']
        num_events = options['events']

        self.stdout.write(self.style.SUCCESS(f'Création de {num_users} utilisateurs et {num_events} événements...'))

        # Listes de données pour la génération aléatoire
        noms = ['Martin', 'Bernard', 'Dubois', 'Thomas', 'Robert', 'Richard', 'Petit', 'Durand', 'Leroy', 'Moreau',
                'Simon', 'Laurent', 'Lefebvre', 'Michel', 'Garcia', 'David', 'Bertrand', 'Roux', 'Vincent', 'Fournier',
                'Morel', 'Girard', 'Andre', 'Lefevre', 'Mercier', 'Dupont', 'Lambert', 'Bonnet', 'Francois', 'Martinez']

        prenoms = ['Jean', 'Pierre', 'Michel', 'André', 'Philippe', 'René', 'Louis', 'Alain', 'Jacques', 'Bernard',
                 'Marcel', 'Daniel', 'Roger', 'Robert', 'Claude', 'Paul', 'Christian', 'Henri', 'Georges', 'Nicolas',
                 'Marie', 'Nathalie', 'Isabelle', 'Sylvie', 'Catherine', 'Françoise', 'Anne', 'Monique', 'Martine', 'Jacqueline']

        voitures = ['Chevrolet Camaro', 'Ford Mustang', 'Dodge Challenger', 'Pontiac GTO', 'Chevrolet Corvette',
                   'Cadillac Eldorado', 'Jeep Wrangler', 'Dodge Charger', 'Ford Thunderbird', 'Buick Riviera',
                   'Chevrolet Impala', 'Plymouth Barracuda', 'Ford GT40', 'Dodge Viper', 'Shelby Cobra']

        villes = ['Paris', 'Marseille', 'Lyon', 'Toulouse', 'Nice', 'Nantes', 'Strasbourg', 'Montpellier',
                 'Bordeaux', 'Lille', 'Rennes', 'Reims', 'Saint-Étienne', 'Toulon', 'Angers', 'Grenoble']

        lieux_evenements = [
            'Place de la Concorde', 'Esplanade du Trocadéro', 'Circuit de Nevers Magny-Cours',
            'Parking du centre commercial', 'Champ de Mars', 'Circuit Paul Ricard', 'Parking du Stade',
            'Place de la République', 'Boulevard de la Mer', 'Avenue des Champs-Élysées'
        ]

        types_evenements = ['rasso', 'other']

        descriptions_evenements = [
            "Venez nombreux pour notre rassemblement mensuel de voitures américaines. Ambiance conviviale et passionnée garantie!",
            "Grande exposition de muscle cars, hot rods et customs. Concours d'élégance et prix à gagner.",
            "Journée découverte et initiation pour les amateurs de voitures américaines. Venez avec votre famille!",
            "Rassemblement nocturne avec concert live et expositions de véhicules personnalisés.",
            "Rencontre entre passionnés, discussions techniques et échanges d'expériences. Barbecue offert!",
            "Exposition photo de voitures de collection américaines. Experts présents pour répondre à vos questions.",
            "Sortie route légendaire sur nos plus belles nationales. Circuit d'environ 150 km avec pauses panoramiques.",
            "Atelier mécanique et restauration : conseils et démonstrations par nos membres expérimentés."
        ]

        bios = [
            "Passionné de Mustang depuis toujours, je collectionne les modèles 65-70.",
            "Amateur de hot rods et customs, je travaille sur une Impala 64 depuis 3 ans.",
            "Mécanicien de formation, spécialisé dans les V8 américains.",
            "Fan de muscle cars, je possède une Challenger R/T 1970 restaurée.",
            "Nouveau dans le monde des américaines, je viens d'acquérir ma première Camaro.",
            "Collectionneur depuis 30 ans, je possède 6 voitures américaines d'exception.",
            "Passionné de road trips, j'ai traversé les États-Unis avec ma Corvette.",
            "Je restaure des voitures vintage américaines et je fais des expositions.",
            "Amoureux de la culture US et de ses belles mécaniques depuis mon premier voyage en Californie.",
            "Photographe automobile spécialisé dans les américaines des années 60-70."
        ]

        with transaction.atomic():
            # 1. Création des utilisateurs
            existing_users_count = User.objects.count() - 1  # Exclure le superutilisateur
            users_to_create = max(0, num_users - existing_users_count)

            self.stdout.write(f'Création de {users_to_create} nouveaux utilisateurs...')

            new_users = []
            for i in range(users_to_create):
                prenom = random.choice(prenoms)
                nom = random.choice(noms)
                username = f"{prenom.lower()}{i+existing_users_count+1}"

                user = User.objects.create_user(
                    username=username,
                    email=f"{username}@example.com",
                    password="password123",  # Mot de passe simple pour test
                    first_name=prenom,
                    last_name=nom
                )

                # Personnalisation du profil
                profile = user.profile
                profile.is_approved = True
                profile.bio = random.choice(bios) if random.random() > 0.3 else None
                profile.role = random.choices(['member', 'member', 'developer'], weights=[0.85, 0.85, 0.15])[0]

                # Réseaux sociaux (seulement pour certains)
                if random.random() > 0.5:
                    profile.instagram = f"https://instagram.com/{username}"
                if random.random() > 0.6:
                    profile.facebook = f"https://facebook.com/{username}"
                if random.random() > 0.8:
                    profile.twitter = f"https://twitter.com/{username}"

                # Couleur de bannière personnalisée pour certains
                if random.random() > 0.7:
                    profile.banner_color = '#' + ''.join(random.choice('0123456789ABCDEF') for _ in range(6))
                    profile.banner_approved = True

                # Téléchargement d'une image de profil aléatoire
                # 80% des utilisateurs auront une image de profil personnalisée
                if random.random() < 0.8:
                    # On utilise différents services pour varier les styles d'avatars
                    avatar_services = [
                        # Avatars réalistes générés
                        f"https://avatars.dicebear.com/api/avataaars/{username}.png",
                        # Avatars de personnes (plus réalistes)
                        f"https://avatars.dicebear.com/api/personas/{username}.png",
                        # Avatars d'identité (plus abstraits)
                        f"https://api.dicebear.com/7.x/identicon/png?seed={username}",
                        # Avatars avec des options supplémentaires
                        f"https://api.dicebear.com/7.x/bottts/png?seed={username}&backgroundColor=random"
                    ]

                    avatar_url = random.choice(avatar_services)

                    try:
                        self.stdout.write(f"Téléchargement d'avatar pour {username}...")
                        response = requests.get(avatar_url, timeout=5)
                        if response.status_code == 200:
                            # Générer un nom de fichier unique basé sur le nom d'utilisateur
                            hash_obj = hashlib.md5(username.encode())
                            filename = f"{hash_obj.hexdigest()}.png"

                            # Sauvegarder l'image dans le champ profile_image
                            profile.profile_image.save(
                                filename,
                                ContentFile(response.content),
                                save=False  # Ne pas encore sauvegarder le modèle
                            )
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"Erreur lors du téléchargement d'avatar: {e}"))

                profile.save()
                new_users.append(user)

            self.stdout.write(self.style.SUCCESS(f'{len(new_users)} utilisateurs créés avec succès!'))

            # 2. Création des événements
            existing_events_count = Event.objects.count()
            events_to_create = max(0, num_events - existing_events_count)

            self.stdout.write(f'Création de {events_to_create} nouveaux événements...')

            now = timezone.now()

            new_events = []
            for i in range(events_to_create):
                # Répartir les événements entre passés et futurs
                if random.random() > 0.4:  # 60% futurs, 40% passés
                    # Événement futur (1 à 180 jours dans le futur)
                    days_ahead = random.randint(1, 180)
                    event_date = now + timedelta(days=days_ahead, hours=random.randint(0, 12))
                else:
                    # Événement passé (1 à 300 jours dans le passé)
                    days_ago = random.randint(1, 300)
                    event_date = now - timedelta(days=days_ago, hours=random.randint(0, 12))

                ville = random.choice(villes)
                lieu = random.choice(lieux_evenements)
                type_evenement = random.choice(types_evenements)

                # Titre plus descriptif selon le type
                if type_evenement == 'rasso':
                    titre = f"Rassemblement de {random.choice(voitures)} à {ville}"
                else:
                    titre = f"Exposition de {random.choice(voitures)} - {ville}"

                location = f"{lieu}, {ville}"

                event = Event.objects.create(
                    title=titre,
                    description=random.choice(descriptions_evenements),
                    location=location,
                    event_date=event_date,
                    is_published=True,
                    type=type_evenement
                )
                new_events.append(event)

            self.stdout.write(self.style.SUCCESS(f'{len(new_events)} événements créés avec succès!'))

            # 3. Ajout de participants aux événements
            all_users = list(User.objects.exclude(is_superuser=True))
            all_events = list(Event.objects.all())

            self.stdout.write('Ajout de participants aux événements...')
            participants_count = 0

            # Supprimer les participants existants pour éviter les doublons
            EventParticipant.objects.all().delete()

            for event in all_events:
                # Sélectionner entre 5 et 20 participants aléatoires pour chaque événement
                num_participants = random.randint(5, min(20, len(all_users)))
                event_participants = random.sample(all_users, num_participants)

                for user in event_participants:
                    # Ajouter une vérification pour les événements passés
                    # Seuls les événements futurs ou récemment passés ont des participants
                    if event.event_date > now - timedelta(days=60):
                        EventParticipant.objects.create(event=event, user=user)
                        participants_count += 1

            self.stdout.write(self.style.SUCCESS(f'{participants_count} participations ajoutées aux événements!'))

        self.stdout.write(self.style.SUCCESS('Peuplement de la base de données terminé avec succès!'))
