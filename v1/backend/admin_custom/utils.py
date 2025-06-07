from django.contrib.contenttypes.models import ContentType
from .models import ChangeHistory, AdminNotification
import json
from django.utils import timezone
from datetime import timedelta

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def create_admin_notification(notification_type, title, message, user=None, content_object=None):
    """Create an admin notification"""
    content_type = None
    object_id = None

    if content_object:
        content_type = ContentType.objects.get_for_model(content_object)
        # Handle different primary key types for notifications
        try:
            object_id = str(content_object.pk)  # Convert to string instead of int
        except:
            object_id = None

    notification = AdminNotification.objects.create(
        type=notification_type,
        title=title,
        message=message,
        user=user,
        content_type=content_type,
        object_id=object_id
    )

    print(f"Created notification: {notification.title} for user: {user}")
    return notification

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

    # SIMPLE BANNER NOTIFICATION: Check for banner_approved change from True to False
    if (field_changes and
        'banner_approved' in field_changes and
        field_changes['banner_approved'].get('old') == 'True' and
        field_changes['banner_approved'].get('new') == 'False'):

        # Get the profile user (handle different profile models)
        profile_user = None
        if hasattr(instance, 'user'):
            profile_user = instance.user
        elif hasattr(instance, 'owner'):
            profile_user = instance.owner

        if profile_user:
            # Create notification directly
            try:
                AdminNotification.objects.create(
                    type='banner_request',
                    title=f'Nouvelle demande de bannière - {profile_user.username}',
                    message=f'{profile_user.get_full_name() or profile_user.username} a uploadé une nouvelle bannière qui nécessite une approbation.',
                    user=profile_user,
                    content_type=ContentType.objects.get_for_model(instance),
                    object_id=str(instance.pk)
                )
                print(f"✅ Banner notification created for user: {profile_user.username}")
            except Exception as e:
                print(f"❌ Error creating banner notification: {e}")

    # Handle new user registrations
    if (actor_type == 'user' and
        instance._meta.model_name in ['profile', 'userprofile'] and
        action == 'create' and
        user and user.is_authenticated):

        create_admin_notification(
            notification_type='user_registration',
            title=f'Nouvelle inscription - {user.username}',
            message=f'{user.get_full_name() or user.username} s\'est inscrit et attend l\'approbation.',
            user=user,
            content_object=instance
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

def check_banner_submission(profile_instance, user):
    """Check if a banner needs approval and create notification"""
    try:
        # Check if profile has a banner and it's not approved
        banner_field = getattr(profile_instance, 'banner', None) or getattr(profile_instance, 'banner_image', None)
        is_approved = getattr(profile_instance, 'banner_approved', True) or getattr(profile_instance, 'is_banner_approved', True)

        # If there's a banner and it's not approved, create notification
        if banner_field and not is_approved:
            # Check if we already have a recent notification for this user
            recent_notification = AdminNotification.objects.filter(
                type='banner_request',
                user=user,
                created_at__gte=timezone.now() - timedelta(minutes=5)
            ).exists()

            if not recent_notification:
                create_admin_notification(
                    notification_type='banner_request',
                    title=f'Demande de bannière en attente - {user.username}',
                    message=f'{user.get_full_name() or user.username} a une bannière en attente d\'approbation.',
                    user=user,
                    content_object=profile_instance
                )
    except Exception as e:
        print(f"Error checking banner submission: {e}")
