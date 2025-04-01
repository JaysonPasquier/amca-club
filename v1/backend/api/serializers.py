from rest_framework import serializers
from django.contrib.auth.models import User
from accounts.models import UserProfile, Newsletter
from core.models import Event, ClubInfo

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'profile_image', 'member_id', 'role', 'role_display', 'date_created', 'instagram', 'facebook', 'twitter']

class EventSerializer(serializers.ModelSerializer):
    is_past_event = serializers.BooleanField(read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'location', 'event_date', 'is_past_event']

class ClubInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubInfo
        fields = ['name', 'description', 'founder_info', 'cofounder_info', 'email', 'phone', 'instagram', 'facebook', 'twitter']

class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = ['email']
