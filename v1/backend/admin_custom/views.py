from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.apps import apps
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms.models import modelform_factory
from django.http import JsonResponse

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@user_passes_test(is_admin)
def admin_dashboard(request):
    """Custom admin dashboard"""
    # Get all models from your apps (excluding Django's built-in apps)
    custom_apps = ['core', 'events', 'members']  # Add your app names here
    models_info = []

    for app_name in custom_apps:
        try:
            app = apps.get_app_config(app_name)
            for model in app.get_models():
                models_info.append({
                    'name': model._meta.verbose_name_plural,
                    'model_name': model.__name__,
                    'app_name': app_name,
                    'count': model.objects.count(),
                    'url_name': f'admin_model_list',
                })
        except:
            pass

    context = {
        'models_info': models_info,
        'title': 'Administration'
    }
    return render(request, 'admin_custom/dashboard.html', context)

@user_passes_test(is_admin)
def model_list(request, app_name, model_name):
    """List view for any model"""
    try:
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

    # Get field names for table headers
    fields = [f for f in model._meta.fields if not f.name == 'id']

    context = {
        'model': model,
        'model_name': model_name,
        'app_name': app_name,
        'objects': page_obj,
        'fields': fields,
        'search_query': search_query,
        'title': f"{model._meta.verbose_name_plural} Administration"
    }
    return render(request, 'admin_custom/model_list.html', context)

@user_passes_test(is_admin)
def model_add(request, app_name, model_name):
    """Add new object view"""
    try:
        model = apps.get_model(app_name, model_name)
    except:
        messages.error(request, f"Model {model_name} not found")
        return redirect('admin_dashboard')

    # Create dynamic form
    ModelForm = modelform_factory(model, exclude=[])

    if request.method == 'POST':
        form = ModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
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
        model = apps.get_model(app_name, model_name)
    except:
        messages.error(request, f"Model {model_name} not found")
        return redirect('admin_dashboard')

    obj = get_object_or_404(model, pk=pk)
    ModelForm = modelform_factory(model, exclude=[])

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
        model = apps.get_model(app_name, model_name)
    except:
        return JsonResponse({'success': False, 'error': 'Model not found'})

    obj = get_object_or_404(model, pk=pk)

    if request.method == 'POST':
        obj.delete()
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})
