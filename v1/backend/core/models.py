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
