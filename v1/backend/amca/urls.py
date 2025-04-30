from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import newsletter_signup
from core.views import shop_home, shop_products, product_detail

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    # Ajouter les URLs du forum ici
    path('forum/', include('forum.urls', namespace='forum')),
    path('newsletter/signup/', newsletter_signup, name='newsletter_signup'),

    # Shop URLs
    path('shop/', shop_home, name='shop_home'),
    path('shop/products/', shop_products, name='shop_products'),
    path('shop/product/<slug:slug>/', product_detail, name='product_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
