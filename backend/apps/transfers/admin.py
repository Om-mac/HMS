from django.contrib import admin
from .models import PatientAccess, PermissionToken, TransferRequest


@admin.register(PatientAccess)
class PatientAccessAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'patient', 'status', 'access_level', 'requested_at', 'valid_until']
    list_filter = ['status', 'access_level']
    search_fields = ['doctor__user__first_name', 'patient__user__first_name']


@admin.register(PermissionToken)
class PermissionTokenAdmin(admin.ModelAdmin):
    list_display = ['access', 'valid_until', 'is_revoked', 'times_used']
    list_filter = ['is_revoked']


@admin.register(TransferRequest)
class TransferRequestAdmin(admin.ModelAdmin):
    list_display = ['patient', 'requesting_doctor', 'receiving_doctor', 'transfer_type', 'status', 'created_at']
    list_filter = ['status', 'transfer_type', 'urgency']
    search_fields = ['patient__user__first_name']
