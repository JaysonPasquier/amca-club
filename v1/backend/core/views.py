from django.shortcuts import render
from django.utils import timezone
from accounts.forms import NewsletterForm
from accounts.models import UserProfile
from .models import Event, ClubInfo

def home(request):
    """Homepage view with club info, events, and newsletter signup"""
    # Get club information
    club_info = ClubInfo.objects.first()

    # Get upcoming events (published only)
    upcoming_events = Event.objects.filter(
        is_published=True,
        event_date__gte=timezone.now()
    ).order_by('event_date')[:3]

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
