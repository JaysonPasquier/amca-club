from django.contrib import admin
from .models import Event, ClubInfo

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    # Update to use is_past_event_admin instead of is_past_event
    list_display = ('title', 'location', 'event_date', 'is_published', 'is_past_event_admin')
    list_filter = ('is_published', 'event_date')
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'event_date'

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'location')
        }),
        ('Informations de Date', {
            'fields': ('event_date',)
        }),
        ('Publication', {
            'fields': ('is_published',)
        }),
    )

@admin.register(ClubInfo)
class ClubInfoAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Fondateurs', {
            'fields': ('founder_info', 'cofounder_info')
        }),
        ('Informations de Contact', {
            'fields': ('email', 'phone', 'instagram', 'facebook', 'twitter')
        }),
    )

    def has_add_permission(self, request):
        # Only allow one instance of ClubInfo
        return not ClubInfo.objects.exists()
