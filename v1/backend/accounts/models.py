from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator
# Don't import the custom storage class anymore
# from .storage import PermissionFileStorage
import os
import uuid

def get_file_path(instance, filename):
    """
    Generate a unique filename for uploads to avoid permission issues
    """
    ext = filename.split('.')[-1]
    # Create a unique filename with uuid to avoid collisions
    new_filename = f"{uuid.uuid4().hex}.{ext}"
    return new_filename

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('founder', 'Fondateur'),
        ('co-founder', 'Co-Fondateur'),
        ('member', 'Membre'),
        ('developer', 'Développeur'),
        ('admin', 'Administratif')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_image = models.ImageField(
        upload_to=get_file_path,  # Use our custom function
        # Don't use custom storage
        default='default.png',
        blank=True
    )
    member_id = models.PositiveIntegerField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    is_approved = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)
    instagram = models.CharField(max_length=100, blank=True, null=True)
    facebook = models.CharField(max_length=100, blank=True, null=True)
    twitter = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True, verbose_name="Biographie")

    # Nouveaux champs pour la bannière
    banner_image = models.ImageField(
        upload_to=get_file_path,  # Use our custom function
        # Don't use custom storage
        blank=True,
        null=True
    )
    banner_color = models.CharField(max_length=20, blank=True, null=True, default="#2c3e50", verbose_name="Couleur de bannière")
    banner_approved = models.BooleanField(default=False, verbose_name="Bannière approuvée")

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.get_role_display()}"

    def save(self, *args, **kwargs):
        if not self.member_id:
            # Generate a sequential member ID
            last_profile = UserProfile.objects.all().order_by('-member_id').first()
            if last_profile:
                self.member_id = last_profile.member_id + 1
            else:
                self.member_id = 1
        super().save(*args, **kwargs)

    def get_banner_style(self):
        """Retourne le style CSS pour la bannière en fonction des paramètres approuvés"""
        if self.banner_approved and self.banner_image:
            return f"background-image: url('{self.banner_image.url}'); background-size: cover; background-position: center;"
        elif self.banner_approved and self.banner_color:
            return f"background-color: {self.banner_color};"
        else:
            return "background: linear-gradient(45deg, #2c3e50, #3498db);" # Style par défaut

class SignupRequest(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=128, blank=True)  # For storing hashed password
    date_requested = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default(False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.date_requested.strftime('%d-%m-%Y')}"

class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='posts/', null=True, blank=True)
    video = models.FileField(upload_to='posts/videos/', null=True, blank=True,
                            validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'avi', 'mkv'])])
    description = models.TextField(blank=True, null=True)
    is_approved = models.BooleanField(default=False, verbose_name="Approuvé")
    approval_date = models.DateTimeField(blank=True, null=True, verbose_name="Date d'approbation")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post by {self.user.username} on {self.created_at.strftime('%Y-%m-%d')}"

    class Meta:
        ordering = ['-created_at']

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post}"

    class Meta:
        ordering = ['created_at']

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"Like by {self.user.username} on {self.post}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
