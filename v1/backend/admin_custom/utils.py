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

    # Special handling for banner changes on user profiles
    if (actor_type == 'user' and
        instance._meta.model_name in ['profile', 'userprofile'] and
        field_changes):

        # Check if banner field was changed
        banner_changed = False
        banner_field_names = ['banner', 'banner_image', 'profile_banner']

        for field_name in banner_field_names:
            if field_name in field_changes:
                old_value = field_changes[field_name].get('old')
                new_value = field_changes[field_name].get('new')

                # Banner was added or changed (not removed)
                if new_value and new_value != old_value and new_value != 'None':
                    banner_changed = True
                    break

        # Check if banner approval was reset to False (indicates new banner pending approval)
        banner_approval_reset = False
        approval_field_names = ['banner_approved', 'is_banner_approved']

        for field_name in approval_field_names:
            if field_name in field_changes:
                old_value = field_changes[field_name].get('old')
                new_value = field_changes[field_name].get('new')

                # Approval was reset to False (new banner submitted)
                if new_value == 'False' and old_value != new_value:
                    banner_approval_reset = True
                    break

        # Create notification for banner change request
        if banner_changed or banner_approval_reset:
            # Check if there's already a recent notification for this user to avoid duplicates
            from django.utils import timezone
            from datetime import timedelta

            recent_notification = AdminNotification.objects.filter(
                type='banner_request',
                user=user,
                created_at__gte=timezone.now() - timedelta(minutes=5)
            ).exists()

            if not recent_notification:
                create_admin_notification(
                    notification_type='banner_request',
                    title=f'Nouvelle demande de bannière - {user.username}',
                    message=f'{user.get_full_name() or user.username} a uploadé une nouvelle bannière et attend l\'approbation.',
                    user=user,
                    content_object=instance
                )

    # Also handle new user registrations
    if (actor_type == 'user' and
        instance._meta.model_name in ['profile', 'userprofile'] and
        action == 'create'):

        create_admin_notification(
            notification_type='user_registration',
            title=f'Nouvelle inscription - {user.username}',
            message=f'{user.get_full_name() or user.username} s\'est inscrit et attend l\'approbation.',
            user=user,
            content_object=instance
        )

def create_admin_notification(notification_type, title, message, user=None, content_object=None):
    """Create an admin notification"""
    content_type = None
    object_id = None

    if content_object:
        content_type = ContentType.objects.get_for_model(content_object)
        # Handle different primary key types for notifications too
        try:
            object_id = content_object.pk
            if isinstance(object_id, str):
                try:
                    object_id = int(object_id)
                except (ValueError, TypeError):
                    object_id = None  # Set to None if can't convert to int
        except:
            object_id = None

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
