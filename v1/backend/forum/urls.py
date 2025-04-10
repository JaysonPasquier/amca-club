from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    # Pages principales
    path('', views.forum_home, name='forum_home'),
    path('categorie/<slug:slug>/', views.category_detail, name='category_detail'),
    path('sujet/<slug:slug>/', views.topic_detail, name='topic_detail'),

    # Actions de création/édition
    path('nouveau-sujet/', views.create_topic, name='create_topic'),
    path('nouveau-sujet/<slug:category_slug>/', views.create_topic, name='create_topic_in_category'),
    path('sujet/<slug:slug>/modifier/', views.edit_topic, name='edit_topic'),
    path('sujet/<slug:topic_slug>/repondre/', views.create_reply, name='create_reply'),
    path('reponse/<int:reply_id>/solution/', views.mark_solution, name='mark_solution'),
]
