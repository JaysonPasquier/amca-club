from django.contrib.contenttypes.models import ContentType
from .models import ChangeHistory, AdminNotification
import json

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def track_model_change(instance, action, user=None, request=None, field_changes=None):
    """Track changes to models"""

    # Skip tracking for certain models that we don't want to track
    if instance._meta.label in ['sessions.Session', 'admin.LogEntry', 'admin_custom.ChangeHistory']:
        return

    # Get object_id, handle different primary key types
    try:
        object_id = instance.pk
        # Convert to int if possible, otherwise skip tracking for non-integer PKs
        if isinstance(object_id, str):
            try:
                object_id = int(object_id)
            except (ValueError, TypeError):
                # Skip tracking for models with non-integer primary keys (like sessions)
                return
    except:
        return

    # Determine actor type - Fix the logic
    actor_type = 'system'  # Default
    if user and user.is_authenticated:
        if user.is_staff or user.is_superuser:
            actor_type = 'admin'
        else:
            actor_type = 'user'

    # Get request info if available
    ip_address = None
    user_agent = ''
    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

    # Create change history record
    ChangeHistory.objects.create(
        action=action,
        actor_type=actor_type,
        user=user if user and user.is_authenticated else None,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=object_id,
        object_repr=str(instance)[:200],
        field_changes=field_changes or {},
        ip_address=ip_address,
        user_agent=user_agent[:500] if user_agent else ''
    )

    # Create admin notifications for user profile changes (banner/avatar)
    if (actor_type == 'user' and
        instance._meta.model_name in ['profile', 'userprofile'] and
        field_changes and
        any(field in ['banner', 'avatar', 'profile_picture'] for field in field_changes.keys())):

        changed_fields = [field for field in field_changes.keys() if field in ['banner', 'avatar', 'profile_picture']]
        field_names = ', '.join(changed_fields)

        create_admin_notification(
            notification_type='profile_change',
            title=f'Modification de profil - {user.username}',
            message=f'{user.username} a modifié son profil ({field_names}). Vérification recommandée.',
            user=user,
            content_object=instance
        )

def create_admin_notification(notification_type, title, message, user=None, content_object=None):
    """Create an admin notification"""
    content_type = None
    object_id = None

    if content_object:
        content_type = ContentType.objects.get_for_model(content_object)
        object_id = content_object.pk

    AdminNotification.objects.create(
        type=notification_type,
        title=title,
        message=message,
        user=user,
        content_type=content_type,
        object_id=object_id
    )

def track_banner_request(user, banner_image, description):
    """Track banner approval request"""
    from .models import BannerRequest

    banner_request = BannerRequest.objects.create(
        user=user,
        banner_image=banner_image,
        description=description
    )

    # Create notification for admins
    create_admin_notification(
        notification_type='banner_approval',
        title=f'Nouvelle demande de bannière',
        message=f'{user.username} a soumis une nouvelle bannière pour approbation.',
        user=user,
        content_object=banner_request
    )

    return banner_request
