from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.forms import NewsletterForm
from accounts.models import UserProfile
from .models import Event, ClubInfo, EventParticipant, Product, ProductCategory, ProductVariation, ProductImage
from django.contrib.auth.decorators import user_passes_test
import json

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

    # Prepare color-specific images map
    color_images = {}
    for color in colors:
        # Use color's own image as front image if available, otherwise use product's main image
        front_image = color.image.url if color.image else product.image.url

        color_images[color.name] = {
            'front': front_image,
            'back': None,  # Will be populated if back image found
            'additional': []
        }

        # Search for additional images for this color
        for img in product_images:
            img_name = img.image.name.lower()
            color_name_lower = color.name.lower()

            if color_name_lower in img_name:
                # Check if it's a back image
                if 'back' in img_name or 'dos' in img_name or 'arriere' in img_name:
                    color_images[color.name]['back'] = img.image.url
                else:
                    # If not specifically marked as back, add to additional
                    color_images[color.name]['additional'].append(img.image.url)

    # Convert color_images to JSON-safe format (ensure Python None is converted to JS null)
    for color_name, images in color_images.items():
        if images['back'] is None:
            images['back'] = "null"  # This will be converted to JS null

    # Get variation data organized by color and size for JS
    variation_data = {}
    for variation in variations:
        if variation.color.name not in variation_data:
            variation_data[variation.color.name] = {}

        variation_data[variation.color.name][variation.size.size] = {
            'price': float(variation.get_price()),
            'stock': variation.stock,
            'sku': variation.sku or '',
        }

    context = {
        'product': product,
        'related_products': related_products,
        'colors': colors,
        'sizes': sizes,
        'variations': variations,
        'variation_data': json.dumps(variation_data),
        'color_images': json.dumps(color_images),
        'active_shop': True,
    }

    return render(request, 'core/shop/product_detail.html', context)
