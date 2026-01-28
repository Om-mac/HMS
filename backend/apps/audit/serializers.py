"""
Serializers for audit logs.
"""
from rest_framework import serializers
from .models import AuditLog, DataExportLog


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit logs."""
    
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name', 'user_email', 'user_type',
            'action', 'resource_type', 'resource_id', 'patient_id',
            'description', 'changes', 'ip_address', 'user_agent',
            'request_path', 'request_method', 'reason', 'timestamp'
        ]


class DataExportLogSerializer(serializers.ModelSerializer):
    """Serializer for data export logs."""
    
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = DataExportLog
        fields = [
            'id', 'user', 'user_name', 'export_type', 'resource_type',
            'record_count', 'filters_applied', 'file_name', 'file_size',
            'ip_address', 'timestamp'
        ]
