from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('events/', views.events, name='events'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/toggle-participation/', views.toggle_event_participation, name='toggle_event_participation'),
    path('social/', views.social_links, name='social_links'),
    # Custom admin URLs - better to put this in main project urls.py
    path('custom-admin/', include('admin_custom.urls')),
]
