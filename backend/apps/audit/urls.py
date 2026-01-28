"""
URL patterns for audit logs.
"""
from django.urls import path
from .views import AuditLogListView, PatientAuditLogView, DataExportLogListView

app_name = 'audit'

urlpatterns = [
    path('logs/', AuditLogListView.as_view(), name='log_list'),
    path('logs/patient/<str:patient_id>/', PatientAuditLogView.as_view(), name='patient_logs'),
    path('exports/', DataExportLogListView.as_view(), name='export_list'),
]
