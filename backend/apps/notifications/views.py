"""
Views for notification management.
"""
from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404

from .models import Notification, NotificationTemplate
from .serializers import NotificationSerializer, NotificationTemplateSerializer


class NotificationListView(generics.ListAPIView):
    """List notifications for the current user."""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).order_by('-created_at')


class NotificationDetailView(generics.RetrieveAPIView):
    """Get notification details."""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


class NotificationTemplateListView(generics.ListAPIView):
    """List notification templates (admin only)."""
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = NotificationTemplate.objects.filter(is_active=True)


class NotificationTemplateCreateView(generics.CreateAPIView):
    """Create notification template (admin only)."""
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAdminUser]
