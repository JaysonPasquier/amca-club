from django.contrib import admin
from .models import Event, ClubInfo, EventParticipant, ProductCategory, Product, ProductImage

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'event_date', 'type', 'is_published', 'is_past_event_admin')
    list_filter = ('is_published', 'event_date', 'type')
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'event_date'

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'location', 'type')
        }),
        ('Informations de Date', {
            'fields': ('event_date',)
        }),
        ('Publication', {
            'fields': ('is_published',)
        }),
        ('Flyer', {
            'fields': ['flyer_front', 'flyer_back'],
            'classes': ['collapse'],
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

@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'joined_at')
    list_filter = ('event', 'joined_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'event__title')
    date_hierarchy = 'joined_at'
    raw_id_fields = ('user', 'event')

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_featured', 'stock', 'is_active')
    list_filter = ('category', 'is_featured', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'slug', 'description', 'category')
        }),
        ('Prix', {
            'fields': ('price', 'old_price')
        }),
        ('Images', {
            'fields': ('image',)
        }),
        ('Stock', {
            'fields': ('stock', 'available_sizes')
        }),
        ('Options', {
            'fields': ('is_featured', 'is_active')
        }),
    )
