"""
Serializers for notifications.
"""
from rest_framework import serializers
from .models import Notification, NotificationTemplate


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for notification templates."""
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'template_type', 'channel',
            'whatsapp_template_id', 'subject', 'body',
            'available_variables', 'is_active'
        ]


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications."""
    
    template_name = serializers.CharField(source='template.name', read_only=True)
    recipient_name = serializers.CharField(source='recipient.full_name', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'template', 'template_name', 'recipient', 'recipient_name',
            'channel', 'recipient_contact', 'subject', 'body', 'status',
            'appointment', 'sent_at', 'delivered_at', 'read_at',
            'error_message', 'created_at'
        ]
        read_only_fields = ['id', 'sent_at', 'delivered_at', 'read_at', 'created_at']
