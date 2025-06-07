from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.apps import apps
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms.models import modelform_factory
from django.http import JsonResponse
from django.contrib.auth.models import User

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@user_passes_test(is_admin)
def admin_dashboard(request):
    """Custom admin dashboard"""
    models_info = []

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

    # Define custom model mappings with French names
    model_mappings = {
        'core': {
            'ClubInfo': 'Informations du Club',
            'Event': 'Événements',
        },
        'accounts': {
            'Profile': 'Profils Utilisateurs',
            'Newsletter': 'Abonnés Newsletter',
        },
        'forum': {
            'Topic': 'Sujets du Forum',
            'Post': 'Messages du Forum',
            'Category': 'Catégories du Forum',
        }
    }

    # Dynamically discover and add models
    for app_name, model_names in model_mappings.items():
        try:
            app_config = apps.get_app_config(app_name)
            for model in app_config.get_models():
                model_name = model.__name__
                if model_name in model_names:
                    try:
                        models_info.append({
                            'name': model_names[model_name],
                            'model_name': model_name,
                            'app_name': app_name,
                            'count': model.objects.count(),
                            'url_name': 'admin_model_list',
                        })
                    except Exception as e:
                        print(f"Error counting {app_name}.{model_name}: {e}")
        except Exception as e:
            print(f"App {app_name} not available: {e}")
            continue

    # Debug: Print what we found
    print("Found models:")
    for model_info in models_info:
        print(f"  - {model_info['name']} ({model_info['app_name']}.{model_info['model_name']}): {model_info['count']} items")

    context = {
        'models_info': models_info,
        'title': 'Administration'
    }
    return render(request, 'admin_custom/dashboard.html', context)

@user_passes_test(is_admin)
def model_list(request, app_name, model_name):
    """List view for any model"""
    try:
        if app_name == 'auth' and model_name == 'User':
            model = User
        else:
            model = apps.get_model(app_name, model_name)
    except:
        messages.error(request, f"Model {model_name} not found")
        return redirect('admin_dashboard')

    # Search functionality
    search_query = request.GET.get('search', '')
    objects = model.objects.all()

    if search_query:
        # Simple search across all text fields
        search_fields = [f.name for f in model._meta.fields if f.get_internal_type() in ['CharField', 'TextField']]
        if search_fields:
            query = Q()
            for field in search_fields:
                query |= Q(**{f"{field}__icontains": search_query})
            objects = objects.filter(query)

    # Pagination
    paginator = Paginator(objects, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get field names for table headers (exclude sensitive fields for User model)
    if model == User:
        # Only show safe fields for User model
        fields = [f for f in model._meta.fields if f.name in ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined']]
    else:
        fields = [f for f in model._meta.fields if not f.name == 'id']

    # Prepare objects with field values for easier template rendering
    objects_with_values = []
    for obj in page_obj:
        obj_data = {
            'object': obj,
            'field_values': []
        }
        for field in fields:
            try:
                value = getattr(obj, field.name)
                if value is None:
                    display_value = "-"
                elif len(str(value)) > 50:
                    display_value = str(value)[:47] + "..."
                else:
                    display_value = str(value)
                obj_data['field_values'].append(display_value)
            except AttributeError:
                obj_data['field_values'].append("-")
        objects_with_values.append(obj_data)

    context = {
        'model': model,
        'model_name': model_name,
        'app_name': app_name,
        'objects': page_obj,
        'objects_with_values': objects_with_values,
        'fields': fields,
        'search_query': search_query,
        'title': f"{model._meta.verbose_name_plural} Administration"
    }
    return render(request, 'admin_custom/model_list.html', context)

@user_passes_test(is_admin)
def model_add(request, app_name, model_name):
    """Add new object view"""
    try:
        if app_name == 'auth' and model_name == 'User':
            model = User
        else:
            model = apps.get_model(app_name, model_name)
    except:
        messages.error(request, f"Model {model_name} not found")
        return redirect('admin_dashboard')

    # Create dynamic form with excluded fields
    excluded_fields = []
    if model == User:
        # Exclude sensitive fields for User model
        excluded_fields = ['password', 'user_permissions', 'groups', 'last_login']

    ModelForm = modelform_factory(model, exclude=excluded_fields)

    if request.method == 'POST':
        form = ModelForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save()
            # Set default password for new users
            if model == User and not obj.password:
                obj.set_password('defaultpassword123')
                obj.save()
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
    """Edit object view"""
    try:
        if app_name == 'auth' and model_name == 'User':
            model = User
        else:
            model = apps.get_model(app_name, model_name)
    except:
        messages.error(request, f"Model {model_name} not found")
        return redirect('admin_dashboard')

    obj = get_object_or_404(model, pk=pk)

    # Create dynamic form with excluded fields
    excluded_fields = []
    if model == User:
        # Exclude sensitive fields for User model
        excluded_fields = ['password', 'user_permissions', 'groups', 'last_login']

    ModelForm = modelform_factory(model, exclude=excluded_fields)

    if request.method == 'POST':
        form = ModelForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
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
    """Delete object view"""
    try:
        if app_name == 'auth' and model_name == 'User':
            model = User
        else:
            model = apps.get_model(app_name, model_name)
    except:
        messages.error(request, f"Model {model_name} not found")
        return redirect('admin_dashboard')















    return render(request, 'admin_custom/model_delete.html', context)    }        'title': f"Supprimer {model._meta.verbose_name}"        'app_name': app_name,        'model_name': model_name,        'object': obj,    context = {        return redirect('admin_model_list', app_name=app_name, model_name=model_name)        messages.success(request, f"{model._meta.verbose_name} supprimé avec succès!")        obj.delete()    if request.method == 'POST':    obj = get_object_or_404(model, pk=pk)        return JsonResponse({'success': False, 'error': 'Model not found'})

    obj = get_object_or_404(model, pk=pk)

    if request.method == 'POST':
        obj.delete()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})
