from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'events', views.EventViewSet)
router.register(r'members', views.MemberViewSet)
router.register(r'club-info', views.ClubInfoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('subscribe/', views.NewsletterSubscribeView.as_view(), name='api-subscribe'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
