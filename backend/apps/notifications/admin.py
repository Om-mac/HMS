from django.contrib import admin
from .models import Notification, NotificationTemplate


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'channel', 'is_active']
    list_filter = ['template_type', 'channel', 'is_active']
    search_fields = ['name']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'channel', 'status', 'sent_at', 'created_at']
    list_filter = ['channel', 'status', 'created_at']
    search_fields = ['recipient__email', 'recipient_contact']
    date_hierarchy = 'created_at'
