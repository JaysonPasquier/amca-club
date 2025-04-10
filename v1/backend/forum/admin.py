from django.contrib import admin
from .models import ForumCategory, ForumTopic, ForumReply

@admin.register(ForumCategory)
class ForumCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'get_topic_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    ordering = ('order', 'name')

@admin.register(ForumTopic)
class ForumTopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'created_at', 'is_pinned', 'is_locked', 'views', 'get_replies_count')
    list_filter = ('category', 'is_pinned', 'is_locked', 'created_at')
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'

@admin.register(ForumReply)
class ForumReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'topic', 'author', 'created_at', 'is_solution')
    list_filter = ('is_solution', 'created_at')
    search_fields = ('content', 'author__username', 'topic__title')
    date_hierarchy = 'created_at'
