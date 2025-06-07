from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .utils import track_model_change, create_admin_notification
import threading

# Thread-local storage to get request context
_local = threading.local()

def set_current_request(request):
    """Store current request in thread-local storage"""
    _local.request = request

def get_current_request():
    """Get current request from thread-local storage"""
    return getattr(_local, 'request', None)

@receiver(post_save)
def track_model_save(sender, instance, created, **kwargs):
    """Track model saves automatically"""
    # Skip tracking for our own tracking models to avoid recursion
    if sender.__name__ in ['ChangeHistory', 'AdminNotification']:
        return

    request = get_current_request()
    user = getattr(request, 'user', None) if request else None

    action = 'create' if created else 'update'
    track_model_change(instance, action, user, request)

    # Create notifications for specific events
    if created:
        if sender == User:
            create_admin_notification(
                notification_type='user_registration',
                title='Nouvel utilisateur',
                message=f'Un nouvel utilisateur {instance.username} s\'est inscrit.',
                user=instance
            )

@receiver(post_delete)
def track_model_delete(sender, instance, **kwargs):
    """Track model deletions automatically"""
    if sender.__name__ in ['ChangeHistory', 'AdminNotification']:
        return

    request = get_current_request()
    user = getattr(request, 'user', None) if request else None

    track_model_change(instance, 'delete', user, request)
