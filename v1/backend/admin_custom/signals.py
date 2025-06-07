from django.db.models.signals import post_save, post_delete, pre_save
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

@receiver(pre_save)
def store_original_values(sender, instance, **kwargs):
    """Store original values before saving to track changes"""
    if instance.pk:  # Only for existing objects
        try:
            original = sender.objects.get(pk=instance.pk)
            instance._original_values = {}

            for field in instance._meta.fields:
                if not field.name.startswith('_'):  # Skip private fields
                    instance._original_values[field.name] = getattr(original, field.name, None)
        except sender.DoesNotExist:
            instance._original_values = {}
    else:
        instance._original_values = {}

@receiver(post_save)
def track_model_save(sender, instance, created, **kwargs):
    """Track model saves with proper change detection"""
    # Get user and request from thread local storage
    current_request = getattr(_local, 'request', None)
    user = getattr(current_request, 'user', None) if current_request else None

    # Determine action
    action = 'create' if created else 'update'

    # Track field changes for updates
    field_changes = {}
    if not created and hasattr(instance, '_original_values'):
        for field in instance._meta.fields:
            field_name = field.name
            if field_name in instance._original_values:
                old_value = instance._original_values[field_name]
                new_value = getattr(instance, field_name, None)

                # Convert values to strings for comparison
                old_str = str(old_value) if old_value is not None else None
                new_str = str(new_value) if new_value is not None else None

                if old_str != new_str:
                    field_changes[field_name] = {
                        'old': old_str,
                        'new': new_str
                    }

    track_model_change(instance, action, user, current_request, field_changes)

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
