from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.forms import NewsletterForm
from accounts.models import UserProfile
from .models import Event, ClubInfo, EventParticipant, Product, ProductCategory, ProductVariation, ProductImage
from django.contrib.auth.decorators import user_passes_test
import json
import re

def home(request):
    """Homepage view with club info, events, and newsletter signup"""
    # Get club information
    club_info = ClubInfo.objects.first()

    # Get upcoming events (published only)
    # Modifier ici pour récupérer 6 événements au lieu de 3
    upcoming_events = Event.objects.filter(
        is_published=True,
        event_date__gte=timezone.now()
    ).order_by('event_date')[:6]  # Augmenté de 3 à 6

    # Get founders and co-founders for display
    founders = UserProfile.objects.filter(
        is_approved=True,
        role='founder'
    ).select_related('user')

    cofounders = UserProfile.objects.filter(
        is_approved=True,
        role='co-founder'
    ).select_related('user')

    # Newsletter signup form
    newsletter_form = NewsletterForm()

    context = {
        'club_info': club_info,
        'upcoming_events': upcoming_events,
        'founders': founders,
        'cofounders': cofounders,
        'newsletter_form': newsletter_form,
    }

    return render(request, 'core/home.html', context)

def about(request):
    """About page with more detailed club information"""
    club_info = ClubInfo.objects.first()

    context = {
        'club_info': club_info,
    }

    return render(request, 'core/about.html', context)

def events(request):
    """List all upcoming and past events"""
    now = timezone.now()

    upcoming_events = Event.objects.filter(
        is_published=True,
        event_date__gte=now
    ).order_by('event_date')

    past_events = Event.objects.filter(
        is_published=True,
        event_date__lt=now
    ).order_by('-event_date')

    context = {
        'upcoming_events': upcoming_events,
        'past_events': past_events,
    }

    return render(request, 'core/events.html', context)

def event_detail(request, event_id):
    """Show details for a specific event"""
    event = get_object_or_404(Event, id=event_id, is_published=True)

    # Get latest upcoming events for sidebar
    upcoming_events = Event.objects.filter(
        is_published=True,
        event_date__gte=timezone.now()
    ).exclude(id=event_id).order_by('event_date')[:3]

    # Get event participants
    participants = UserProfile.objects.filter(
        user__in=event.participants.values_list('user', flat=True),
        is_approved=True
    ).select_related('user').order_by('-user__profile__member_id')

    context = {
        'event': event,
        'upcoming_events': upcoming_events,
        'participants': participants,
        'is_participating': event.is_user_participating(request.user),
        'participants_count': event.get_participants_count()
    }

    return render(request, 'core/event_detail.html', context)

@login_required
def toggle_event_participation(request, event_id):
    """Toggle user participation in an event"""
    event = get_object_or_404(Event, id=event_id, is_published=True)

    # Check if user is already participating
    participation = EventParticipant.objects.filter(event=event, user=request.user)

    if participation.exists():
        # User was already participating, so remove them
        participation.delete()
        messages.success(request, "Vous ne participez plus à cet événement.")
    else:
        # User just joined
        EventParticipant.objects.create(event=event, user=request.user)
        messages.success(request, "Vous participez maintenant à cet événement!")

    return redirect('event_detail', event_id=event_id)

def social_links(request):
    """
    View for displaying social media links page accessible via QR code.
    """
    return render(request, 'core/social_links.html')

def is_admin(user):
    return user.is_authenticated and user.is_staff

# Shop views with admin access control
@user_passes_test(is_admin, login_url='home')
def shop_home(request):
    """Shop home page showing featured products"""
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]
    categories = ProductCategory.objects.all()

    return render(request, 'core/shop/shop_home.html', {
        'featured_products': featured_products,
        'categories': categories,
        'active_shop': True,
    })

@user_passes_test(is_admin, login_url='home')
def shop_products(request):
    """Shop products page with filtering options"""
    products = Product.objects.filter(is_active=True)
    categories = ProductCategory.objects.all()

    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    # Filter by price range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Sort products
    sort_by = request.GET.get('sort')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')

    return render(request, 'core/shop/shop_products.html', {
        'products': products,
        'categories': categories,
        'active_shop': True,
        'current_category': category_slug,
        'current_sort': sort_by,
        'min_price': min_price,
        'max_price': max_price,
    })

@user_passes_test(is_admin, login_url='home')
def product_detail(request, slug):
    """Product detail page"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]

    # Get available variations
    variations = ProductVariation.objects.filter(product=product)
    colors = product.get_available_colors()
    sizes = product.get_available_sizes()

    # Get all product images
    product_images = product.images.all()

    # Determine default color (prefer "Blanc" or "White" if available, otherwise the first color)
    default_color = None
    for color in colors:
        clean_color_name = re.sub(r'-back$', '', color.name.lower())
        if clean_color_name in ['blanc', 'white']:
            default_color = color
            break

    if not default_color and colors.exists():
        default_color = colors.first()

    # Group colors to remove duplicates caused by front/back naming
    unique_colors = {}
    for color in colors:
        clean_name = re.sub(r'-back$', '', color.name)
        if clean_name not in unique_colors:
            unique_colors[clean_name] = color

    # Prepare color-specific images map
    color_images = {}
    for color_name, color in unique_colors.items():
        # Use color's own image as front image if available, otherwise use product's main image
        front_image = color.image.url if color.image else product.image.url

        color_images[color_name] = {
            'front': front_image,
            'back': None,
            'left': None,
            'right': None,
            'additional': []
        }

        # First, check for images that have explicit view_type and color association
        color_specific_views = ProductImage.objects.filter(product=product, color=color)
        for view in color_specific_views:
            if view.view_type in ['front', 'back', 'left', 'right']:
                color_images[color_name][view.view_type] = view.image.url

        # Also check other images using naming convention (for backward compatibility)
        for img in product_images:
            img_name = img.image.name.lower()
            color_name_lower = color_name.lower()

            if color_name_lower in img_name:
                # Check view type from filename
                if 'back' in img_name or 'dos' in img_name or 'arriere' in img_name:
                    if not color_images[color_name]['back']:  # Don't override if already set
                        color_images[color_name]['back'] = img.image.url
                elif 'left' in img_name or 'gauche' in img_name or 'cote-g' in img_name:
                    if not color_images[color_name]['left']:
                        color_images[color_name]['left'] = img.image.url
                elif 'right' in img_name or 'droite' in img_name or 'cote-d' in img_name:
                    if not color_images[color_name]['right']:
                        color_images[color_name]['right'] = img.image.url
                elif not any(word in img_name for word in ['front', 'face', 'avant']) and not color_images[color_name]['front'] == img.image.url:
                    # If not specifically marked as a view and not already the front image, add to additional
                    color_images[color_name]['additional'].append(img.image.url)

        # Check for images from "-back" variant colors (backward compatibility)
        back_color_name = f"{color_name}-back"
        for c in colors:
            if c.name.lower() == back_color_name.lower() and c.image:
                if not color_images[color_name]['back']:  # Don't override if already set
                    color_images[color_name]['back'] = c.image.url

    # Convert color_images to JSON-safe format
    for color_name, images in color_images.items():
        for key, value in images.items():
            if value is None and key != 'additional':
                images[key] = "null"

    # Get variation data organized by color and size for JS
    variation_data = {}
    for variation in variations:
        # Remove any "-back" suffix for the color key
        color_name = re.sub(r'-back$', '', variation.color.name)

        if color_name not in variation_data:
            variation_data[color_name] = {}

        variation_data[color_name][variation.size.size] = {
            'price': float(variation.get_price()),
            'stock': variation.stock,
            'sku': variation.sku or '',
        }

    context = {
        'product': product,
        'related_products': related_products,
        'colors': list(unique_colors.values()),  # Use only unique colors
        'sizes': sizes,
        'variations': variations,
        'variation_data': json.dumps(variation_data),
        'color_images': json.dumps(color_images),
        'default_color': default_color.name if default_color else '',
        'active_shop': True,
    }

    return render(request, 'core/shop/product_detail.html', context)
