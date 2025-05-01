from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Event(models.Model):
    EVENT_TYPE_CHOICES = (
        ('rasso', 'Rassemblement'),
        ('other', 'Autre'),
        # D'autres types pourront être ajoutés ici ultérieurement
    )

    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    location = models.CharField(max_length=200, verbose_name="Lieu")
    event_date = models.DateTimeField(verbose_name="Date de l'événement")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    is_published = models.BooleanField(default=False, verbose_name="Est publié")
    type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='other', verbose_name="Type d'événement")
    flyer_front = models.ImageField(upload_to='event_flyers/', null=True, blank=True, verbose_name="Flyer (recto)")
    flyer_back = models.ImageField(upload_to='event_flyers/', null=True, blank=True, verbose_name="Flyer (verso)")

    def __str__(self):
        return self.title

    @property
    def is_past_event(self):
        return self.event_date < timezone.now()

    # Add a method for admin display instead of trying to set attributes on a property
    def is_past_event_admin(self):
        return self.event_date < timezone.now()
    is_past_event_admin.short_description = "Événement passé"
    is_past_event_admin.boolean = True

    def get_participants_count(self):
        """Retourne le nombre de participants à l'événement"""
        return self.participants.count()

    def is_user_participating(self, user):
        """Vérifie si l'utilisateur participe à l'événement"""
        if not user or not user.is_authenticated:
            return False
        return self.participants.filter(user=user).exists()

    class Meta:
        ordering = ['event_date']
        verbose_name = "Événement"
        verbose_name_plural = "Événements"

class EventParticipant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')
        verbose_name = "Participant à l'événement"
        verbose_name_plural = "Participants aux événements"

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.event.title}"

class ClubInfo(models.Model):
    name = models.CharField(max_length=100, default="Club de Voitures Américaines", verbose_name="Nom")
    description = models.TextField(verbose_name="Description")
    founder_info = models.TextField(blank=True, null=True, verbose_name="Informations sur le fondateur")
    cofounder_info = models.TextField(blank=True, null=True, verbose_name="Informations sur le co-fondateur")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone")
    instagram = models.CharField(max_length=100, blank=True, null=True)
    facebook = models.CharField(max_length=100, blank=True, null=True)
    twitter = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Information du Club"
        verbose_name_plural = "Informations du Club"

# New Shop models
class ProductCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom de la catégorie")
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    order = models.IntegerField(default=0, verbose_name="Ordre d'affichage")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Catégorie de produit"
        verbose_name_plural = "Catégories de produits"
        ordering = ['order', 'name']

class Product(models.Model):
    SIZE_CHOICES = (
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
        ('XXXL', 'XXXL'),
        ('unique', 'Taille unique'),
    )

    name = models.CharField(max_length=200, verbose_name="Nom du produit")
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name="Description")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix")
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Ancien prix")
    image = models.ImageField(upload_to='products/', verbose_name="Image principale")
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products', verbose_name="Catégorie")
    stock = models.PositiveIntegerField(default=0, verbose_name="Stock disponible")
    is_featured = models.BooleanField(default=False, verbose_name="Produit en vedette")
    is_active = models.BooleanField(default=True, verbose_name="Produit actif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    available_sizes = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tailles disponibles")

    def __str__(self):
        return self.name

    @property
    def discount_percentage(self):
        if self.old_price and self.old_price > self.price:
            return int(100 - (self.price * 100 / self.old_price))
        return 0

    @property
    def get_available_sizes(self):
        if not self.available_sizes:
            return []
        return self.available_sizes.split(',')

    def get_available_colors(self):
        return ProductColor.objects.filter(product=self).order_by('name')

    def get_available_sizes(self):
        return ProductSize.objects.filter(product=self).order_by('order')

    def get_all_variations(self):
        return ProductVariation.objects.filter(product=self)

    def has_variations(self):
        return self.get_all_variations().exists()

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['-created_at']

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/', verbose_name="Image")
    is_main = models.BooleanField(default=False, verbose_name="Image principale")

    def __str__(self):
        return f"Image pour {self.product.name}"

    class Meta:
        verbose_name = "Image de produit"
        verbose_name_plural = "Images de produit"

class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='colors')
    name = models.CharField(max_length=50)  # e.g., "Red", "Blue"
    color_code = models.CharField(max_length=10, blank=True)  # Hex color code
    image = models.ImageField(upload_to='products/colors/', blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        ordering = ['name']
        unique_together = ['product', 'name']

class ProductSize(models.Model):
    SIZE_CHOICES = [
        ('XS', 'Extra Small'),
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
        ('XXL', '2X Large'),
        ('XXXL', '3X Large'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes')
    size = models.CharField(max_length=10, choices=SIZE_CHOICES)
    order = models.PositiveSmallIntegerField(default=0)  # For consistent ordering

    def __str__(self):
        return self.get_size_display()

    class Meta:
        ordering = ['order']
        unique_together = ['product', 'size']

class ProductVariation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    color = models.ForeignKey(ProductColor, on_delete=models.CASCADE)
    size = models.ForeignKey(ProductSize, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} - {self.color.name} - {self.size.size}"

    def get_price(self):
        return self.price if self.price is not None else self.product.price

    class Meta:
        unique_together = ['product', 'color', 'size']
