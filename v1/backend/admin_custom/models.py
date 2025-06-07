from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class AdminNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('user_action', 'Action utilisateur'),
        ('system_alert', 'Alerte système'),
        ('banner_request', 'Demande de bannière'),
        ('user_registration', 'Inscription utilisateur'),
        ('profile_change', 'Modification de profil'),
        ('content_moderation', 'Modération de contenu'),
    ]

    type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Generic foreign key to link to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"

class ChangeHistory(models.Model):
    ACTION_CHOICES = [
        ('create', 'Créé'),
        ('update', 'Modifié'),
        ('delete', 'Supprimé'),
    ]

    ACTOR_CHOICES = [
        ('admin', 'Administrateur'),
        ('user', 'Utilisateur'),
        ('system', 'Système'),
    ]

    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    actor_type = models.CharField(max_length=10, choices=ACTOR_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # What was changed
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    object_repr = models.CharField(max_length=200)

    # Change details
    field_changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['actor_type']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        actor = self.user.username if self.user else 'Système'
        return f"{actor} a {self.get_action_display()} {self.object_repr}"

class BannerRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    banner_image = models.ImageField(upload_to='banner_requests/')
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_banners')
    rejection_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-requested_at']

    def __str__(self):
        return f"Bannière de {self.user.username} - {self.get_status_display()}"
