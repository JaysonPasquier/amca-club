from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.apps import apps
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms.models import modelform_factory
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import AdminNotification, ChangeHistory, BannerRequest
from .utils import track_model_change, create_admin_notification
from django.utils import timezone
from django.db.models.fields.related import ForeignKey, OneToOneField, ManyToManyField

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@user_passes_test(is_admin)
def admin_dashboard(request):
    """Custom admin dashboard"""
    models_info = []

    # Models to exclude (the ones you don't want to see)
    excluded_models = {
        # Shop/Product related models (different possible app names)
        'shop.ProductCategory',
        'shop.Product',
        'shop.ProductColor',
        'shop.ProductImage',
        'shop.ProductSize',
        'shop.ProductVariation',
        'core.ProductCategory',
        'core.Product',
        'core.ProductColor',
        'core.ProductImage',
        'core.ProductSize',
        'core.ProductVariation',
        # Django built-in models we don't want to manage
        'admin.LogEntry',
        'auth.Permission',
        'auth.Group',
        'contenttypes.ContentType',
        'sessions.Session',
        'django.contrib.admin.LogEntry',
        'django.contrib.auth.Permission',
        'django.contrib.auth.Group',
        'django.contrib.contenttypes.ContentType',
        'django.contrib.sessions.Session',
    }

    # Also exclude by model name regardless of app (as backup)
    excluded_model_names = {
        'ProductCategory',
        'Product',
        'ProductColor',
        'ProductImage',
        'ProductSize',
        'ProductVariation',
        'Permission',
        'Group',
        'ContentType',
        'Session',
        'LogEntry',
    }

    # Custom display names for models (French translations)
    model_display_names = {
        'auth.User': 'Utilisateurs',
        'core.ClubInfo': 'Informations du Club',
        'core.Event': 'Événements',
        'accounts.UserProfile': 'Profils Utilisateurs',  # Changed from Profile to UserProfile
        'accounts.SignupRequest': 'Demandes d\'inscription',
        'accounts.Newsletter': 'Abonnés Newsletter',
        'forum.Topic': 'Sujets du Forum',
        'forum.Post': 'Messages du Forum',
        'forum.Category': 'Catégories du Forum',
        'api.ApiKey': 'Clés API',
        # Add more custom names as needed
    }

    # Add Django's User model first
    try:
        user_model = User
        models_info.append({
            'name': 'Utilisateurs',
            'model_name': 'User',
            'app_name': 'auth',
            'count': user_model.objects.count(),
            'url_name': 'admin_model_list',
        })
    except:
        pass

    # Get all installed apps and their models
    for app_config in apps.get_app_configs():
        app_name = app_config.name

        # Skip Django's built-in apps we don't want to manage
        if app_name in ['django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
                       'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
                       'rest_framework', 'corsheaders', 'crispy_forms', 'crispy_bootstrap5']:
            continue

        for model in app_config.get_models():
            model_key = f"{app_name}.{model.__name__}"

            # Skip excluded models by full path
            if model_key in excluded_models:
                continue

            # Skip excluded models by name only
            if model.__name__ in excluded_model_names:
                continue

            # Skip User model as we already added it
            if model_key == 'auth.User':
                continue

            try:
                # Get display name (custom or default)
                display_name = model_display_names.get(model_key, model._meta.verbose_name_plural)

                models_info.append({
                    'name': display_name,
                    'model_name': model.__name__,  # This will be UserProfile for the accounts.UserProfile model
                    'app_name': app_name,
                    'count': model.objects.count(),
                    'url_name': 'admin_model_list',
                })
            except Exception as e:
                print(f"Error with model {model_key}: {e}")
                continue

    # Sort models alphabetically by display name
    models_info.sort(key=lambda x: x['name'])

    # Get pending notifications count
    pending_notifications = AdminNotification.objects.filter(is_read=False).count()
    pending_banners = BannerRequest.objects.filter(status='pending').count()

    # Get pending signup requests count
    from accounts.models import SignupRequest
    pending_signup_requests = SignupRequest.objects.filter(is_approved=False, is_rejected=False).count()

    context = {
        'models_info': models_info,
        'title': 'Administration',
        'pending_notifications': pending_notifications,
        'pending_banners': pending_banners,
        'pending_signup_requests': pending_signup_requests,
    }
    return render(request, 'admin_custom/dashboard.html', context)

@user_passes_test(is_admin)
def admin_notifications(request):
    """View admin notifications"""
    notifications = AdminNotification.objects.all().order_by('-created_at')[:50]

    # Mark as read if requested
    if request.GET.get('mark_read'):
        AdminNotification.objects.filter(is_read=False).update(is_read=True)
        messages.success(request, 'Toutes les notifications ont été marquées comme lues.')
        return redirect('admin_notifications')

    # Count unread notifications
    unread_count = AdminNotification.objects.filter(is_read=False).count()

    context = {
        'notifications': notifications,
        'unread_count': unread_count,
        'title': 'Notifications'
    }
    return render(request, 'admin_custom/notifications.html', context)

@user_passes_test(is_admin)
def change_history(request):
    """View change history"""
    history_type = request.GET.get('type', 'all')

    history = ChangeHistory.objects.all()

    if history_type == 'admin':
        history = history.filter(actor_type='admin')
    elif history_type == 'user':
        history = history.filter(actor_type__in=['user', 'system'])

    # Pagination
    paginator = Paginator(history, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'history': page_obj,
        'history_type': history_type,
        'title': 'Historique des modifications'
    }
    return render(request, 'admin_custom/change_history.html', context)

@user_passes_test(is_admin)
def banner_requests(request):
    """Manage banner requests"""
    status_filter = request.GET.get('status', 'pending')

    requests = BannerRequest.objects.all()
    if status_filter != 'all':
        requests = requests.filter(status=status_filter)

    context = {
        'banner_requests': requests,
        'status_filter': status_filter,
        'title': 'Demandes de bannière'
    }
    return render(request, 'admin_custom/banner_requests.html', context)

@user_passes_test(is_admin)
def approve_banner(request, banner_id):
    """Approve or reject banner request"""
    banner_request = get_object_or_404(BannerRequest, id=banner_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'approve':
            banner_request.status = 'approved'
            banner_request.reviewed_by = request.user
            banner_request.reviewed_at = timezone.now()

            # Apply banner to user profile (you'll need to implement this based on your Profile model)
            # profile = banner_request.user.profile
            # profile.banner = banner_request.banner_image
            # profile.save()

            track_model_change(banner_request, 'update', request.user, request)
            messages.success(request, f'Bannière de {banner_request.user.username} approuvée.')

        elif action == 'reject':
            banner_request.status = 'rejected'
            banner_request.reviewed_by = request.user
            banner_request.reviewed_at = timezone.now()
            banner_request.rejection_reason = request.POST.get('rejection_reason', '')

            track_model_change(banner_request, 'update', request.user, request)
            messages.success(request, f'Bannière de {banner_request.user.username} rejetée.')

        banner_request.save()

    return redirect('banner_requests')

# Override existing views to add change tracking
@user_passes_test(is_admin)
def model_add(request, app_name, model_name):
    """Add new object view with change tracking"""
    try:
        if app_name == 'auth' and model_name == 'User':
            model = User
        else:
            model = apps.get_model(app_name, model_name)
    except:
        messages.error(request, f"Model {model_name} not found")
        return redirect('admin_dashboard')

    excluded_fields = []
    if model == User:
        excluded_fields = ['password', 'user_permissions', 'groups', 'last_login']

    ModelForm = modelform_factory(model, exclude=excluded_fields)

    if request.method == 'POST':
        form = ModelForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save()
            if model == User and not obj.password:
                obj.set_password('defaultpassword123')
                obj.save()

            # Track the change
            track_model_change(obj, 'create', request.user, request)

            messages.success(request, f"{model._meta.verbose_name} créé avec succès!")
            return redirect('admin_model_list', app_name=app_name, model_name=model_name)
    else:
        form = ModelForm()

    context = {
        'form': form,
        'model': model,
        'model_name': model_name,
        'app_name': app_name,
        'title': f"Ajouter {model._meta.verbose_name}"
    }
    return render(request, 'admin_custom/model_form.html', context)

@user_passes_test(is_admin)
def model_edit(request, app_name, model_name, pk):
    """Edit object view with change tracking"""
    try:
        if app_name == 'auth' and model_name == 'User':
            model = User
        else:
            model = apps.get_model(app_name, model_name)
    except:
        messages.error(request, f"Model {model_name} not found")
        return redirect('admin_dashboard')

    obj = get_object_or_404(model, pk=pk)

    # Store original values for change tracking
    original_values = {}
    for field in model._meta.fields:
        if field.name not in ['password', 'user_permissions', 'groups', 'last_login']:
            original_values[field.name] = getattr(obj, field.name)

    excluded_fields = []
    if model == User:
        excluded_fields = ['password', 'user_permissions', 'groups', 'last_login']

    ModelForm = modelform_factory(model, exclude=excluded_fields)

    if request.method == 'POST':
        form = ModelForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            # Track changes
            field_changes = {}
            for field_name, old_value in original_values.items():
                new_value = getattr(obj, field_name)
                if old_value != new_value:
                    field_changes[field_name] = {
                        'old': str(old_value) if old_value is not None else None,
                        'new': str(new_value) if new_value is not None else None
                    }

            form.save()
            track_model_change(obj, 'update', request.user, request, field_changes)

            messages.success(request, f"{model._meta.verbose_name} modifié avec succès!")
            return redirect('admin_model_list', app_name=app_name, model_name=model_name)
    else:
        form = ModelForm(instance=obj)

    context = {
        'form': form,
        'model': model,
        'model_name': model_name,
        'app_name': app_name,
        'object': obj,
        'title': f"Modifier {model._meta.verbose_name}"
    }
    return render(request, 'admin_custom/model_form.html', context)

@user_passes_test(is_admin)
def model_delete(request, app_name, model_name, pk):
    """Delete object view with change tracking"""
    try:
        if app_name == 'auth' and model_name == 'User':
            model = User
        else:
            model = apps.get_model(app_name, model_name)
    except:
        return JsonResponse({'success': False, 'error': 'Model not found'})

    obj = get_object_or_404(model, pk=pk)

    if request.method == 'POST':
        obj_repr = str(obj)
        track_model_change(obj, 'delete', request.user, request)
        obj.delete()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@user_passes_test(is_admin)
def model_list(request, app_name, model_name):
    """List objects for a given model (custom admin changelist)"""
    try:
        if app_name == 'auth' and model_name == 'User':
            model = User
        else:
            model = apps.get_model(app_name, model_name)
    except Exception as e:
        messages.error(request, f"Model {model_name} introuvable ({e})")
        return redirect('admin_dashboard')

    # Search support (simple, on char/text fields)
    search_query = request.GET.get('q', '')
    objects = model.objects.all()

    # DEBUG: Print total count before any filtering
    print(f"DEBUG: Total {model_name} objects before filtering: {objects.count()}")

    if search_query:
        search_fields = []
        for f in model._meta.fields:
            if hasattr(f, 'get_internal_type'):
                field_type = f.get_internal_type()
                if field_type in ['CharField', 'TextField', 'EmailField', 'URLField']:
                    search_fields.append(f.name)

        if search_fields:
            q_objects = Q()
            for field in search_fields:
                q_objects |= Q(**{f"{field}__icontains": search_query})
            objects = objects.filter(q_objects)
            print(f"DEBUG: Objects after search filtering: {objects.count()}")

    # Order by primary key (most recent first)
    try:
        objects = objects.order_by('-pk')
    except Exception as e:
        print(f"DEBUG: Error ordering by pk: {e}")
        objects = objects.order_by('-id')

    # DEBUG: Print objects after ordering
    print(f"DEBUG: Objects after ordering: {objects.count()}")
    print(f"DEBUG: First few objects: {list(objects[:3])}")

    # Pagination
    paginator = Paginator(objects, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # DEBUG: Print pagination info
    print(f"DEBUG: Page object count: {len(page_obj.object_list)}")
    print(f"DEBUG: Page object list: {list(page_obj.object_list)}")

    # Display fields (exclude large text, relations, and sensitive fields)
    display_fields = []
    fields_with_meta = []
    for f in model._meta.fields:
        if (hasattr(f, 'get_internal_type') and
            f.get_internal_type() not in ['TextField', 'BinaryField', 'FileField', 'ImageField'] and
            not isinstance(f, (ForeignKey, OneToOneField, ManyToManyField)) and
            f.name not in ['password', 'user_permissions', 'groups']):
            display_fields.append(f.name)
            fields_with_meta.append(f)

    # Limit to first 6 fields for better display
    display_fields = display_fields[:6]
    fields_with_meta = fields_with_meta[:6]

    # DEBUG: Print display fields
    print(f"DEBUG: Display fields: {display_fields}")

    # Create objects_with_values that the template expects
    objects_with_values = []
    for obj in page_obj.object_list:
        field_values = []
        for field_name in display_fields:
            try:
                value = getattr(obj, field_name)
                if value is None:
                    value = '-'
                elif hasattr(value, '__str__'):
                    value = str(value)[:50]  # Truncate long values
                field_values.append(value)
            except Exception as e:
                field_values.append('-')

        objects_with_values.append({
            'object': obj,
            'field_values': field_values
        })

    # Get total count for the unfiltered queryset
    total_count = model.objects.count()

    context = {
        'model': model,
        'model_name': model_name,
        'app_name': app_name,
        'objects': page_obj,  # Keep for pagination
        'objects_with_values': objects_with_values,  # Add this for template
        'fields': fields_with_meta,  # Add this for template headers
        'display_fields': display_fields,  # Keep for backward compatibility
        'search_query': search_query,
        'title': f"Liste des {model._meta.verbose_name_plural}",
        'total_count': total_count,
        'filtered_count': objects.count(),
    }

    # DEBUG: Print context info
    print(f"DEBUG: Context total_count: {context['total_count']}")
    print(f"DEBUG: Context filtered_count: {context['filtered_count']}")
    print(f"DEBUG: Objects with values count: {len(objects_with_values)}")

    return render(request, 'admin_custom/model_list.html', context)
