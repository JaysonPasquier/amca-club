from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from forum.models import ForumCategory, ForumTopic, ForumReply
import random
import lorem
from datetime import timedelta

class Command(BaseCommand):
    help = 'Génère des posts et des réponses aléatoires dans le forum en utilisant les comptes existants'

    def add_arguments(self, parser):
        parser.add_argument(
            '--topics',
            type=int,
            default=25,
            help='Nombre de sujets à créer'
        )
        parser.add_argument(
            '--replies-min',
            type=int,
            default=3,
            help='Nombre minimum de réponses par sujet'
        )
        parser.add_argument(
            '--replies-max',
            type=int,
            default=15,
            help='Nombre maximum de réponses par sujet'
        )
        parser.add_argument(
            '--pinned-ratio',
            type=float,
            default=0.1,
            help='Pourcentage de sujets épinglés (entre 0 et 1)'
        )
        parser.add_argument(
            '--locked-ratio',
            type=float,
            default=0.05,
            help='Pourcentage de sujets verrouillés (entre 0 et 1)'
        )

    def handle(self, *args, **options):
        num_topics = options['topics']
        replies_min = options['replies_min']
        replies_max = options['replies_max']
        pinned_ratio = options['pinned_ratio']
        locked_ratio = options['locked_ratio']

        self.stdout.write(self.style.SUCCESS(f'Création de {num_topics} sujets avec {replies_min} à {replies_max} réponses...'))

        # Vérification des utilisateurs et catégories disponibles
        users = list(User.objects.filter(is_active=True))
        categories = list(ForumCategory.objects.all())

        if not users:
            self.stdout.write(self.style.ERROR('Aucun utilisateur disponible'))
            return

        if not categories:
            self.stdout.write(self.style.ERROR('Aucune catégorie disponible'))
            return

        # Données pour générer des titres plus réalistes
        marques = [
            'Ford', 'Chevrolet', 'Dodge', 'Cadillac', 'Jeep', 'Pontiac', 'Chrysler',
            'Buick', 'Lincoln', 'GMC', 'Tesla', 'Plymouth', 'Mustang', 'Corvette'
        ]

        modeles = [
            'Mustang', 'Corvette', 'Camaro', 'Challenger', 'Charger', 'Impala', 'Eldorado',
            'Grand Cherokee', 'Escalade', 'F-150', 'Navigator', 'Wrangler', 'Silverado', 'Viper'
        ]

        problemes = [
            'démarrage', 'allumage', 'carburateur', 'freinage', 'suspension', 'transmission',
            'embrayage', 'alternateur', 'climatisation', 'surchauffe', 'pneus', 'échappement',
            'consommation', 'direction', 'électronique', 'boîte de vitesses'
        ]

        questions = [
            'Problème de', 'Comment réparer un', 'Bruit étrange au niveau du', 'Remplacement du',
            'Conseils pour améliorer le', 'Fuite sur le', 'Besoin d\'aide pour un', 'Pièces pour',
            'À vendre', 'Recherche', 'Restauration d\'une', 'Quel est le meilleur', 'Avis sur',
            'Où trouver des pièces pour', 'Comment identifier un problème de'
        ]

        # Générer des titres
        def generate_title():
            if random.random() > 0.7:  # Questions techniques
                return f"{random.choice(questions)} {random.choice(problemes)} sur ma {random.choice(marques)} {random.choice(modeles)} de {random.randint(1960, 2023)}"
            elif random.random() > 0.4:  # Achat/vente
                action = "Vends" if random.random() > 0.5 else "Recherche"
                return f"{action} {random.choice(marques)} {random.choice(modeles)} {random.randint(1960, 2023)}"
            else:  # Discussion générale
                return f"{random.choice(['Avis sur', 'Discussion', 'Votre expérience avec', 'Le meilleur', 'Comparaison'])} {random.choice(marques)} {random.choice(modeles)}"

        # Générer du contenu plus adapté au contexte automobile
        def generate_content():
            paragraphs = random.randint(1, 4)
            content = []

            for _ in range(paragraphs):
                if random.random() > 0.6:
                    content.append(lorem.paragraph())
                else:
                    # Générer du contenu plus spécifique aux voitures
                    sentences = [
                        f"J'ai une {random.choice(marques)} {random.choice(modeles)} de {random.randint(1960, 2023)}.",
                        f"Le problème se situe au niveau du {random.choice(problemes)}.",
                        "Quand je roule à haute vitesse, j'entends un bruit étrange.",
                        "J'ai changé récemment la pièce mais le problème persiste.",
                        "Est-ce que quelqu'un aurait des conseils à me donner ?",
                        "Je cherche une solution économique pour ce problème.",
                        "La voiture a environ 150 000 km au compteur.",
                        "Merci d'avance pour votre aide !",
                        "Je précise que c'est un modèle américain d'origine.",
                        "J'ai déjà essayé de remplacer le filtre et les bougies.",
                        "Le garage m'a dit que ça coûterait très cher à réparer.",
                        "Je suis ouvert à toutes les suggestions !",
                        "Cette voiture est ma première américaine, je ne m'y connais pas encore très bien."
                    ]

                    # Sélectionner certaines phrases aléatoirement
                    selected = random.sample(sentences, k=min(5, random.randint(3, 8)))
                    content.append(" ".join(selected))

            return "\n\n".join(content)

        with transaction.atomic():
            topics_created = 0
            replies_created = 0

            # Créer des sujets avec leurs réponses
            for i in range(num_topics):
                # Sélectionner un utilisateur et une catégorie aléatoirement
                author = random.choice(users)
                category = random.choice(categories)

                # Déterminer si le sujet est épinglé ou verrouillé
                is_pinned = random.random() < pinned_ratio
                is_locked = random.random() < locked_ratio

                # Générer un titre et du contenu
                title = generate_title()
                content = generate_content()

                # Créer le sujet
                topic = ForumTopic(
                    title=title,
                    content=content,
                    author=author,
                    category=category,
                    is_pinned=is_pinned,
                    is_locked=is_locked,
                    views=random.randint(5, 500)  # Nombre de vues aléatoire
                )
                topic.save()  # Utiliser save() pour que le slug soit généré automatiquement
                topics_created += 1

                # Générer des dates aléatoires pour les réponses (entre la date de création du topic et maintenant)
                now = timezone.now()
                topic_created = topic.created_at
                max_days_diff = (now - topic_created).days

                # Nombre de réponses pour ce sujet
                num_replies = random.randint(replies_min, replies_max)

                # Liste pour suivre les réponses créées
                topic_replies = []

                # Créer les réponses
                for j in range(num_replies):
                    reply_author = random.choice(users)
                    # Assurer que la date de réponse est après la date de création du topic
                    days_after = random.randint(0, max(1, max_days_diff))
                    hours_after = random.randint(0, 23)
                    minutes_after = random.randint(0, 59)

                    reply_date = topic_created + timedelta(days=days_after, hours=hours_after, minutes=minutes_after)
                    # S'assurer que la date ne dépasse pas la date actuelle
                    if reply_date > now:
                        reply_date = now - timedelta(minutes=random.randint(1, 60))

                    # Générer le contenu de la réponse
                    reply_content = generate_content()

                    # Créer la réponse
                    reply = ForumReply.objects.create(
                        topic=topic,
                        author=reply_author,
                        content=reply_content,
                        created_at=reply_date
                    )
                    topic_replies.append(reply)
                    replies_created += 1

                # Marquer une réponse comme solution (20% de chance)
                if topic_replies and random.random() < 0.2:
                    solution = random.choice(topic_replies)
                    solution.is_solution = True
                    solution.save()

            self.stdout.write(self.style.SUCCESS(f"Génération terminée: {topics_created} sujets et {replies_created} réponses créés"))
