"""
Views for audit logs.
"""
from rest_framework import generics, permissions
from django.db.models import Q

from .models import AuditLog, DataExportLog
from .serializers import AuditLogSerializer, DataExportLogSerializer


class AuditLogListView(generics.ListAPIView):
    """List audit logs (admin only)."""
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = AuditLog.objects.all()
        
        # Filter by user
        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by patient
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        # Filter by action
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        # Filter by resource type
        resource_type = self.request.query_params.get('resource_type')
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)
        
        # Date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        return queryset.order_by('-timestamp')


class PatientAuditLogView(generics.ListAPIView):
    """List audit logs for a specific patient."""
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        patient_id = self.kwargs.get('patient_id')
        return AuditLog.objects.filter(patient_id=patient_id).order_by('-timestamp')


class DataExportLogListView(generics.ListAPIView):
    """List data export logs (admin only)."""
    serializer_class = DataExportLogSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = DataExportLog.objects.all().order_by('-timestamp')
