"""
Notification models for HMS.
"""
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel


class NotificationTemplate(BaseModel):
    """
    Pre-approved WhatsApp message templates.
    """
    TEMPLATE_TYPES = [
        ('appointment_confirmation', 'Appointment Confirmation'),
        ('appointment_reminder', 'Appointment Reminder'),
        ('appointment_reschedule', 'Appointment Rescheduled'),
        ('appointment_cancellation', 'Appointment Cancelled'),
        ('waitlist_notification', 'Waitlist Slot Available'),
        ('prescription_ready', 'Prescription Ready'),
        ('lab_results', 'Lab Results Available'),
        ('custom', 'Custom Message'),
    ]
    
    CHANNELS = [
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('push', 'Push Notification'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPES)
    channel = models.CharField(max_length=20, choices=CHANNELS, default='whatsapp')
    
    # Meta-approved template ID for WhatsApp
    whatsapp_template_id = models.CharField(max_length=100, blank=True)
    
    # Template content with placeholders
    subject = models.CharField(max_length=200, blank=True)  # For email
    body = models.TextField()
    
    # Available variables like {{patient_name}}, {{doctor_name}}, etc.
    available_variables = models.JSONField(default=list)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'notification_templates'
        ordering = ['template_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.template_type})"
    
    def render(self, context: dict) -> str:
        """Render template with provided context."""
        body = self.body
        for key, value in context.items():
            body = body.replace(f'{{{{{key}}}}}', str(value))
        return body


class Notification(BaseModel):
    """
    Notification log for all sent messages.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]
    
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.SET_NULL,
        null=True,
        related_name='notifications'
    )
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    channel = models.CharField(max_length=20, choices=NotificationTemplate.CHANNELS)
    recipient_contact = models.CharField(max_length=200)  # Phone/Email
    
    subject = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Related entities
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    
    # Delivery tracking
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # External IDs
    external_id = models.CharField(max_length=200, blank=True)  # Twilio SID, etc.
    
    # Error tracking
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.channel} to {self.recipient_contact} - {self.status}"
