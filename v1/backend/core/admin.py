from django.contrib import admin
from .models import Event, ClubInfo, EventParticipant, ProductCategory, Product, ProductImage, ProductColor, ProductSize, ProductVariation, Category

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

class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1

class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1
    autocomplete_fields = ['color', 'size']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'is_featured', 'created_at')
    list_filter = ('is_featured', 'category')
    search_fields = ('name', 'description')
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

@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'color_code', 'product')
    list_filter = ('product',)
    search_fields = ('name', 'product__name')

@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ('size', 'product', 'order')
    list_filter = ('product',)
    search_fields = ('product__name',)

@admin.register(ProductVariation)
class ProductVariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'color', 'size', 'price', 'stock')
    list_filter = ('product', 'color', 'size')
    search_fields = ('product__name', 'color__name')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
