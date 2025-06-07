from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('notifications/', views.admin_notifications, name='admin_notifications'),
    path('history/', views.change_history, name='change_history'),
    path('banner-requests/', views.banner_requests, name='banner_requests'),
    path('banner-requests/<int:banner_id>/approve/', views.approve_banner, name='approve_banner'),
    path('<str:app_name>/<str:model_name>/', views.model_list, name='admin_model_list'),
    path('<str:app_name>/<str:model_name>/add/', views.model_add, name='admin_model_add'),
    path('<str:app_name>/<str:model_name>/<int:pk>/edit/', views.model_edit, name='admin_model_edit'),
    path('<str:app_name>/<str:model_name>/<int:pk>/delete/', views.model_delete, name='admin_model_delete'),
]
