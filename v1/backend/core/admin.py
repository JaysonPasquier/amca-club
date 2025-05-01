from django.contrib import admin
from django.utils.html import mark_safe
from .models import Event, ClubInfo, EventParticipant, ProductCategory, Product, ProductImage, ProductColor, ProductSize, ProductVariation

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
    fields = ('image', 'alt_text', 'is_main')

class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1
    fields = ('name', 'color_code', 'image')

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1
    fields = ('size', 'order')

class ProductVariationInline(admin.StackedInline):
    model = ProductVariation
    extra = 1
    fields = (('color', 'size'), ('price', 'stock'), 'sku')
    autocomplete_fields = ['color', 'size']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'has_variations', 'is_featured', 'created_at')
    list_filter = ('is_featured', 'category', 'created_at')
    search_fields = ('name', 'description', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductColorInline, ProductSizeInline, ProductVariationInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'category')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'old_price', 'stock', 'is_featured')
        }),
        ('Media', {
            'fields': ('image',)
        }),
    )

    def has_variations(self, obj):
        try:
            return ProductVariation.objects.filter(product=obj).exists()
        except Exception:  # This will catch any database errors
            return False
    has_variations.boolean = True
    has_variations.short_description = "Has Variations"

@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_code', 'product', 'color_preview')
    list_filter = ('product',)
    search_fields = ('name', 'product__name')

    def color_preview(self, obj):
        if obj.color_code:
            return mark_safe(f'<div style="background-color: {obj.color_code}; width: 30px; height: 30px; border-radius: 50%;"></div>')
        return "-"
    color_preview.short_description = "Color"

@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'get_size_display', 'order')
    list_filter = ('product', 'size')
    search_fields = ('product__name',)
    ordering = ('product', 'order')

@admin.register(ProductVariation)
class ProductVariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'color', 'size', 'price', 'stock', 'sku')
    list_filter = ('product', 'color', 'size')
    search_fields = ('product__name', 'color__name', 'sku')
    list_editable = ('price', 'stock')

    fieldsets = (
        ('Product Information', {
            'fields': ('product', 'color', 'size')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock', 'sku')
        }),
    )
