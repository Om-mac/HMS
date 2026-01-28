"""
Audit logging models for HIPAA compliance.
"""
from django.db import models
from django.conf import settings
from apps.core.models import UUIDModel
import json


class AuditLog(UUIDModel):
    """
    Comprehensive audit log for all data access and modifications.
    Required for HIPAA compliance.
    """
    ACTION_TYPES = [
        ('create', 'Create'),
        ('read', 'Read'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('export', 'Export'),
        ('print', 'Print'),
        ('access_granted', 'Access Granted'),
        ('access_denied', 'Access Denied'),
        ('access_revoked', 'Access Revoked'),
    ]
    
    RESOURCE_TYPES = [
        ('patient', 'Patient'),
        ('medical_record', 'Medical Record'),
        ('appointment', 'Appointment'),
        ('prescription', 'Prescription'),
        ('medical_file', 'Medical File'),
        ('user', 'User'),
        ('access', 'Access Grant'),
        ('transfer', 'Transfer Request'),
    ]
    
    # Who performed the action
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    user_email = models.EmailField()  # Stored separately in case user is deleted
    user_type = models.CharField(max_length=50)
    
    # What action was performed
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    
    # What resource was affected
    resource_type = models.CharField(max_length=50, choices=RESOURCE_TYPES)
    resource_id = models.CharField(max_length=100)
    
    # Patient involved (for patient-related actions)
    patient_id = models.CharField(max_length=100, blank=True)
    
    # Details
    description = models.TextField()
    
    # What changed (for updates)
    changes = models.JSONField(default=dict, blank=True)
    
    # Request details
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_path = models.CharField(max_length=500, blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    
    # Timestamp
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Reason (for access)
    reason = models.TextField(blank=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['patient_id', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user_email} - {self.action} {self.resource_type} ({self.timestamp})"
    
    @classmethod
    def log(
        cls,
        user,
        action: str,
        resource_type: str,
        resource_id: str,
        description: str,
        patient_id: str = '',
        changes: dict = None,
        request=None,
        reason: str = ''
    ):
        """
        Create an audit log entry.
        
        Args:
            user: The user performing the action
            action: Action type (create, read, update, delete, etc.)
            resource_type: Type of resource (patient, medical_record, etc.)
            resource_id: ID of the resource
            description: Human-readable description
            patient_id: ID of the patient involved (if applicable)
            changes: Dictionary of changes made (for updates)
            request: HTTP request object (for IP and user agent)
            reason: Reason for the action (for access)
        """
        log_entry = cls(
            user=user,
            user_email=user.email if user else 'anonymous',
            user_type=user.user_type if user else 'anonymous',
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            description=description,
            patient_id=str(patient_id) if patient_id else '',
            changes=changes or {},
            reason=reason
        )
        
        if request:
            log_entry.ip_address = cls._get_client_ip(request)
            log_entry.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            log_entry.request_path = request.path[:500]
            log_entry.request_method = request.method
        
        log_entry.save()
        return log_entry
    
    @staticmethod
    def _get_client_ip(request):
        """Extract client IP from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class DataExportLog(UUIDModel):
    """
    Log for all data exports (CSV, PDF, etc.).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='export_logs'
    )
    
    export_type = models.CharField(max_length=50)  # csv, pdf, etc.
    resource_type = models.CharField(max_length=50)
    
    # What was exported
    record_count = models.PositiveIntegerField()
    filters_applied = models.JSONField(default=dict)
    
    # File details
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    
    # Request details
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'data_export_logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user} exported {self.record_count} {self.resource_type} records"
