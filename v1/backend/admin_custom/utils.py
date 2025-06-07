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

    # Determine actor type
    if user and (user.is_staff or user.is_superuser):
        actor_type = 'admin'
    elif user:
        actor_type = 'user'
    else:
        actor_type = 'system'

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
        user=user,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk if hasattr(instance, 'pk') else None,
        object_repr=str(instance)[:200],
        field_changes=field_changes or {},
        ip_address=ip_address,
        user_agent=user_agent[:500] if user_agent else ''
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
