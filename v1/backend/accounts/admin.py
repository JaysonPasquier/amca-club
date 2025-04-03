from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile, SignupRequest, Newsletter

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
        for signup_request in queryset:
            if not signup_request.is_approved and not signup_request.is_rejected:
                # Create a new user
                user = User.objects.create_user(
                    username=signup_request.username,
                    email=signup_request.email,
                    first_name=signup_request.first_name,
                    last_name=signup_request.last_name
                )
                # Set a random password that the user will need to reset
                user.set_password('ChangeMe!2023')
                user.save()

                # Update profile
                profile = user.profile
                profile.is_approved = True
                profile.save()

                # Mark request as approved
                signup_request.is_approved = True
                signup_request.save()

        self.message_user(request, f"{queryset.count()} demande(s) d'inscription approuvée(s).")
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

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
