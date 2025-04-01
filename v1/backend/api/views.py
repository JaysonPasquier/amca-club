from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from accounts.models import UserProfile, Newsletter
from core.models import Event, ClubInfo
from .serializers import EventSerializer, UserProfileSerializer, ClubInfoSerializer, NewsletterSerializer

class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """Point d'API pour visualiser les événements"""
    queryset = Event.objects.filter(is_published=True).order_by('event_date')
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]

class MemberViewSet(viewsets.ReadOnlyModelViewSet):
    """Point d'API pour visualiser les membres"""
    queryset = UserProfile.objects.filter(is_approved=True).order_by('member_id')
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.AllowAny]

class ClubInfoViewSet(viewsets.ReadOnlyModelViewSet):
    """Point d'API pour les informations du club"""
    queryset = ClubInfo.objects.all()
    serializer_class = ClubInfoSerializer
    permission_classes = [permissions.AllowAny]

class NewsletterSubscribeView(APIView):
    """Point d'API pour les abonnements à la newsletter"""
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        serializer = NewsletterSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            # Check if already subscribed
            if Newsletter.objects.filter(email=email).exists():
                return Response({'message': 'Cet email est déjà inscrit.'}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({'message': 'Inscription à la newsletter réussie.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
