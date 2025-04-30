from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('events/', views.events, name='events'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/toggle-participation/', views.toggle_event_participation, name='toggle_event_participation'),
    path('social/', views.social_links, name='social_links'),
]
