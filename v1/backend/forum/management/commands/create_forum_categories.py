from django.core.management.base import BaseCommand
from forum.models import ForumCategory
from django.utils.text import slugify

class Command(BaseCommand):
    help = 'Crée les catégories initiales pour le forum'

    def handle(self, *args, **kwargs):
        # Liste des catégories à créer
        categories = [
            {
                'name': 'Pièces détachées',
                'description': 'Recherche et vente de pièces détachées pour voitures américaines',
                'icon': 'fa-cogs',
                'order': 1
            },
            {
                'name': 'Mécanique',
                'description': 'Questions et conseils sur la mécanique des voitures américaines',
                'icon': 'fa-wrench',
                'order': 2
            },
            {
                'name': 'Restauration',
                'description': 'Projets et conseils de restauration pour véhicules américains',
                'icon': 'fa-paint-brush',
                'order': 3
            },
            {
                'name': 'Achats et ventes',
                'description': 'Annonces de voitures américaines à vendre ou recherche de véhicules',
                'icon': 'fa-tag',
                'order': 4
            },
            {
                'name': 'Événements',
                'description': 'Discussions sur les événements passés et à venir',
                'icon': 'fa-calendar',
                'order': 5
            },
        ]

        created_count = 0
        for category_data in categories:
            # Vérifier si la catégorie existe déjà
            slug = slugify(category_data['name'])
            if not ForumCategory.objects.filter(slug=slug).exists():
                ForumCategory.objects.create(
                    name=category_data['name'],
                    description=category_data['description'],
                    icon=category_data['icon'],
                    order=category_data['order'],
                    slug=slug
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Catégorie '{category_data['name']}' créée avec succès"))
            else:
                self.stdout.write(self.style.WARNING(f"La catégorie '{category_data['name']}' existe déjà"))

        if created_count:
            self.stdout.write(self.style.SUCCESS(f"{created_count} catégories créées"))
        else:
            self.stdout.write(self.style.WARNING("Aucune nouvelle catégorie créée"))
