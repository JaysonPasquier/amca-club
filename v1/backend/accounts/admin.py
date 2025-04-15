from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile, SignupRequest, Newsletter, Post, Comment, Like
from django.utils.html import format_html
from django.db import transaction
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil'
    fields = ('profile_image', 'member_id', 'role', 'is_approved', 'date_created',
              'last_login', 'instagram', 'facebook', 'twitter', 'bio',
              ('banner_image', 'banner_color', 'banner_approved'))
    readonly_fields = ('date_created',)

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_is_approved',
                    'get_member_id', 'get_role', 'get_banner_status')
    list_filter = ('profile__is_approved', 'profile__role', 'profile__banner_approved', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    actions = ['approve_banners', 'reject_banners']

    def get_is_approved(self, obj):
        return obj.profile.is_approved
    get_is_approved.short_description = 'Approuvé'
    get_is_approved.boolean = True

    def get_member_id(self, obj):
        return obj.profile.member_id
    get_member_id.short_description = 'ID Membre'

    def get_role(self, obj):
        return obj.profile.get_role_display()
    get_role.short_description = 'Rôle'

    def get_banner_status(self, obj):
        if obj.profile.banner_image or obj.profile.banner_color != "#2c3e50":
            return obj.profile.banner_approved
        return None
    get_banner_status.short_description = 'Bannière Approuvée'
    get_banner_status.boolean = True

    def approve_banners(self, request, queryset):
        for user in queryset:
            if hasattr(user, 'profile'):
                user.profile.banner_approved = True
                user.profile.save()
        self.message_user(request, f"{queryset.count()} bannières approuvées.")
    approve_banners.short_description = "Approuver les bannières sélectionnées"

    def reject_banners(self, request, queryset):
        for user in queryset:
            if hasattr(user, 'profile'):
                user.profile.banner_approved = False
                user.profile.save()
        self.message_user(request, f"{queryset.count()} bannières rejetées.")
    reject_banners.short_description = "Rejeter les bannières sélectionnées"

@admin.register(SignupRequest)
class SignupRequestAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'date_requested', 'is_approved', 'is_rejected')
    list_filter = ('is_approved', 'is_rejected', 'date_requested')
    search_fields = ('first_name', 'last_name', 'email')
    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        success_count = 0
        error_count = 0

        for signup_request in queryset:
            if not signup_request.is_approved and not signup_request.is_rejected:
                try:
                    with transaction.atomic():
                        # Check if user already exists
                        if User.objects.filter(username=signup_request.username).exists():
                            logger.warning(f"User {signup_request.username} already exists. Skipping.")
                            continue

                        # Use create_user instead of create for proper user creation
                        if signup_request.password:
                            # Create user with existing password hash
                            user = User.objects.create_user(
                                username=signup_request.username,
                                email=signup_request.email,
                                password=None,  # Will set password directly below
                                first_name=signup_request.first_name,
                                last_name=signup_request.last_name,
                            )
                            # Set the hashed password directly
                            user.password = signup_request.password
                        else:
                            # Create user with default password
                            user = User.objects.create_user(
                                username=signup_request.username,
                                email=signup_request.email,
                                password='ChangeMe!2023',
                                first_name=signup_request.first_name,
                                last_name=signup_request.last_name,
                            )

                        # Make sure user is active
                        user.is_active = True
                        user.save()

                        logger.info(f"Successfully created user {user.username} with ID {user.id}")

                        # Update profile
                        if hasattr(user, 'profile'):
                            profile = user.profile
                            profile.is_approved = True
                            profile.save()
                            logger.info(f"Updated profile for user {user.username}")
                        else:
                            logger.error(f"No profile found for user {user.username}")

                        # Mark request as approved
                        signup_request.is_approved = True
                        signup_request.save()

                        success_count += 1
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error approving user {signup_request.username}: {str(e)}")

        if success_count > 0:
            self.message_user(request, f"{success_count} demande(s) d'inscription approuvée(s).")
        if error_count > 0:
            self.message_user(request, f"{error_count} demande(s) d'inscription ont échoué.", level=messages.ERROR)

    approve_requests.short_description = "Approuver les demandes sélectionnées"

    def reject_requests(self, request, queryset):
        queryset.update(is_rejected=True)
        self.message_user(request, f"{queryset.count()} demande(s) d'inscription rejetée(s).")
    reject_requests.short_description = "Rejeter les demandes sélectionnées"

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_subscribed', 'is_active')
    list_filter = ('is_active', 'date_subscribed')
    search_fields = ('email',)
    actions = ['deactivate_subscriptions', 'activate_subscriptions']

    def deactivate_subscriptions(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} abonnement(s) désactivé(s).")
    deactivate_subscriptions.short_description = "Désactiver les abonnements sélectionnés"

    def activate_subscriptions(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} abonnement(s) activé(s).")
    activate_subscriptions.short_description = "Activer les abonnements sélectionnés"

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'has_media', 'is_approved', 'approval_status', 'created_at')
    list_filter = ('is_approved', 'created_at', 'approval_date')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['approve_posts', 'unapprove_posts']
    date_hierarchy = 'created_at'
    list_per_page = 20

    def approval_status(self, obj):
        if obj.is_approved:
            return format_html('<span style="color: green; font-weight: bold;">✓ Approuvé</span>')
        else:
            return format_html('<span style="color: red; font-weight: bold;">⨯ En attente</span>')
    approval_status.short_description = "Statut"

    def has_media(self, obj):
        if obj.image:
            return format_html('<span style="color: green;">✓ Image</span>')
        elif obj.video:
            return format_html('<span style="color: blue;">✓ Vidéo</span>')
        return format_html('<span style="color: gray;">✗ Aucun</span>')
    has_media.boolean = False
    has_media.short_description = "Média"

    def approve_posts(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_approved=True, approval_date=timezone.now())
        self.message_user(request, f"{updated} publication(s) approuvée(s).")
    approve_posts.short_description = "✓ Approuver les publications sélectionnées"

    def unapprove_posts(self, request, queryset):
        updated = queryset.update(is_approved=False, approval_date=None)
        self.message_user(request, f"{updated} publication(s) désapprouvée(s).")
    unapprove_posts.short_description = "⨯ Désapprouver les publications sélectionnées"

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}

        extra_context['title'] = "Gestion des publications"
        extra_context['subtitle'] = "Utilisez les filtres à droite pour afficher les publications en attente d'approbation"

        pending_count = Post.objects.filter(is_approved=False).count()
        if pending_count > 0:
            extra_context['pending_message'] = f"⚠️ {pending_count} publication(s) en attente d'approbation"

        return super().changelist_view(request, extra_context=extra_context)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.order_by('is_approved', '-created_at')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'short_text', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'text')
    date_hierarchy = 'created_at'

    def short_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    short_text.short_description = "Commentaire"

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    date_hierarchy = 'created_at'

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
