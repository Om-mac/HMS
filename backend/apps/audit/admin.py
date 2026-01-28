from django.contrib import admin
from .models import AuditLog, DataExportLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user_email', 'action', 'resource_type', 'timestamp']
    list_filter = ['action', 'resource_type', 'timestamp']
    search_fields = ['user_email', 'description', 'patient_id']
    date_hierarchy = 'timestamp'
    readonly_fields = [
        'user', 'user_email', 'user_type', 'action', 'resource_type',
        'resource_id', 'patient_id', 'description', 'changes',
        'ip_address', 'user_agent', 'request_path', 'timestamp'
    ]


@admin.register(DataExportLog)
class DataExportLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'export_type', 'resource_type', 'record_count', 'timestamp']
    list_filter = ['export_type', 'resource_type', 'timestamp']
    date_hierarchy = 'timestamp'
