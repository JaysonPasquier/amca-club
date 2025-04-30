from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import newsletter_signup

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    # Ajouter les URLs du forum ici
    path('forum/', include('forum.urls', namespace='forum')),
    path('newsletter/signup/', newsletter_signup, name='newsletter_signup'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
