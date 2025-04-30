from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from .models import UserProfile, SignupRequest, Newsletter, Post, Like, Comment
from .forms import SignupRequestForm, UserProfileForm, NewsletterForm
import logging
import traceback
import sys
from django.conf import settings  # Add this import

# Get a logger
logger = logging.getLogger(__name__)

def signup_request(request):
    """Handle user signup requests which need admin approval"""
    if request.method == 'POST':
        form = SignupRequestForm(request.POST)
        if form.is_valid():
            signup_request = form.save(commit=False)
            # Ensure password is properly hashed
            if 'password' in form.cleaned_data:
                signup_request.password = make_password(form.cleaned_data['password'])
            signup_request.save()
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

    # Get user posts - only show approved posts unless viewing own profile
    if user == request.user:
        # User can see all their own posts, including unapproved ones
        posts = Post.objects.filter(user=user).order_by('-created_at')
    else:
        # Others can only see approved posts
        posts = Post.objects.filter(user=user, is_approved=True).order_by('-created_at')

    pending_posts = Post.objects.filter(user=user, is_approved=False).count() if user == request.user else 0

    return render(request, 'accounts/profile.html', {
        'profile_user': user,
        'profile': profile,
        'posts': posts,
        'pending_posts': pending_posts
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
        email = request.POST.get('email')
        if email:
            # Check if the email is already subscribed
            if not Newsletter.objects.filter(email=email).exists():
                # Create the newsletter subscription
                newsletter = Newsletter.objects.create(email=email)

                # Send beautiful HTML email
                subject = "Bienvenue à la Newsletter du Club de Voitures Américaines !"

                # Context data for the email template
                context = {
                    'site_url': settings.SITE_URL,
                    'email': email,
                    'unsubscribe_url': f"{settings.SITE_URL}/newsletter/unsubscribe/?email={email}",
                    'year': timezone.now().year
                }

                # Render HTML content from template
                html_content = render_to_string('emails/welcome_newsletter.html', context)

                # Create plain text version by stripping HTML
                text_content = strip_tags(html_content)

                try:
                    # Create EmailMultiAlternatives for HTML email
                    msg = EmailMultiAlternatives(
                        subject,
                        text_content,
                        settings.DEFAULT_FROM_EMAIL,
                        [email]
                    )
                    # Add these headers to improve deliverability
                    msg.extra_headers = {
                        'List-Unsubscribe': f"<{settings.SITE_URL}/newsletter/unsubscribe/?email={email}>",
                        'Precedence': 'bulk'
                    }
                    # Attach HTML content
                    msg.attach_alternative(html_content, "text/html")
                    # Send email
                    msg.send()

                    print(f"HTML Newsletter email sent successfully to {email}")
                    messages.success(request, "Vous êtes inscrit à notre newsletter ! Un email de confirmation vous a été envoyé.")
                except Exception as e:
                    # Handle errors
                    print(f"Newsletter ERROR: {str(e)}")
                    messages.success(request, "Vous êtes inscrit à notre newsletter !")
            else:
                messages.info(request, "Cette adresse email est déjà inscrite à notre newsletter.")
        else:
            messages.error(request, "Veuillez fournir une adresse email valide.")

    # Redirect back to the previous page or home
    redirect_to = request.META.get('HTTP_REFERER', reverse('home'))
    return redirect(redirect_to)

@login_required
def update_last_login(request):
    """Update the last login time for the user"""
    profile = request.user.profile
    profile.last_login = timezone.now()
    profile.save()
    return redirect('profile')

@login_required
def create_post(request):
    """Create a new post"""
    if request.method == 'POST':
        # Ajouter un débogage pour vérifier la requête
        print("Files in request:", request.FILES)
        print("POST data:", request.POST)

        image = request.FILES.get('image')
        video = request.FILES.get('video')
        description = request.POST.get('description', '')

        # Correction: Vérifier correctement si un fichier est présent
        # et autoriser une plus large gamme de formats
        has_media = 'image' in request.FILES or 'video' in request.FILES

        if not has_media:
            messages.error(request, "Vous devez ajouter une image ou une vidéo.")
            return redirect('profile')

        post = Post.objects.create(
            user=request.user,
            description=description,
            is_approved=False  # Posts need approval by default
        )

        if 'image' in request.FILES:
            post.image = request.FILES['image']
        elif 'video' in request.FILES:
            post.video = request.FILES['video']

        post.save()

        messages.success(request, "Votre publication a été créée et sera visible après approbation par un administrateur.")
        return redirect('profile')

    return redirect('profile')

@login_required
def post_detail(request, post_id):
    """View a specific post"""
    # Add logic to only show approved posts unless it's the post owner
    post = get_object_or_404(Post, id=post_id)

    # Check if post is approved or if user is the owner
    if not post.is_approved and post.user != request.user:
        messages.error(request, "Cette publication n'est pas disponible ou est en attente d'approbation.")
        return redirect('profile')

    comments = post.comments.order_by('created_at')
    liked = post.likes.filter(user=request.user).exists() if request.user.is_authenticated else False

    return render(request, 'accounts/post_detail.html', {
        'post': post,
        'comments': comments,
        'liked': liked
    })

@login_required
def toggle_like_post(request, post_id):
    """Like or unlike a post"""
    post = get_object_or_404(Post, id=post_id)
    like = Like.objects.filter(post=post, user=request.user)

    if like.exists():
        like.delete()
        liked = False
    else:
        Like.objects.create(post=post, user=request.user)
        liked = True

    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes.count()
    })

@login_required
def add_comment(request, post_id):
    """Add a comment to a post"""
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()

        if text:
            comment = Comment.objects.create(
                post=post,
                user=request.user,
                text=text
            )

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'comment_id': comment.id,
                    'user': request.user.get_full_name(),
                    'username': request.user.username,
                    'text': comment.text,
                    'created_at': comment.created_at.strftime('%d/%m/%Y %H:%M')
                })

            return redirect('post_detail', post_id=post.id)

    return redirect('post_detail', post_id=post.id)
