from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.forms import NewsletterForm
from accounts.models import UserProfile
from .models import Event, ClubInfo, EventParticipant

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

    # Add this line to include the API key from settings
    from django.conf import settings

    context = {
        'event': event,
        'upcoming_events': upcoming_events,
        'participants': participants,
        'is_participating': event.is_user_participating(request.user),
        'participants_count': event.get_participants_count(),
        'google_maps_api_key': getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
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
