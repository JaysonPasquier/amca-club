from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import UserProfile, SignupRequest, Newsletter
from .forms import SignupRequestForm, UserProfileForm, NewsletterForm

def signup_request(request):
    """Handle user signup requests which need admin approval"""
    if request.method == 'POST':
        form = SignupRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre demande a été soumise. Un administrateur va examiner votre candidature prochainement.')
            return redirect('home')
    else:
        form = SignupRequestForm()

    return render(request, 'accounts/signup_request.html', {'form': form})

@login_required
def profile_view(request, username=None):
    """View user profile"""
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user

    profile = get_object_or_404(UserProfile, user=user)

    return render(request, 'accounts/profile.html', {
        'profile_user': user,
        'profile': profile
    })

@login_required
def profile_edit(request):
    """Edit user profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre profil a été mis à jour.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.profile)

    return render(request, 'accounts/profile_edit.html', {'form': form})

def members_list(request):
    """Display list of all approved members"""
    # Get all approved members
    members = UserProfile.objects.filter(is_approved=True).order_by('member_id')

    # Ensure members list is complete
    # No need to add any filtering that would exclude members

    # Enable debug to help troubleshoot if needed
    debug = False
    if debug:
        print(f"Total members found: {members.count()}")
        for member in members:
            print(f"Member ID: {member.member_id}, Username: {member.user.username}, Approved: {member.is_approved}")

    return render(request, 'accounts/members_list.html', {
        'members': members,
        'debug': debug
    })

def newsletter_signup(request):
    """Handle newsletter subscriptions"""
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if not Newsletter.objects.filter(email=email).exists():
                form.save()
                messages.success(request, 'Vous êtes bien inscrit à notre newsletter !')
            else:
                messages.info(request, 'Cet email est déjà inscrit.')
            return redirect('home')
    else:
        form = NewsletterForm()

    return render(request, 'accounts/newsletter_signup.html', {'form': form})

@login_required
def update_last_login(request):
    """Update the last login time for the user"""
    profile = request.user.profile
    profile.last_login = timezone.now()
    profile.save()
    return redirect('profile')
