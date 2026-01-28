from django.contrib import admin
from .models import (
    MedicalRecord, MedicalFile, Prescription, PrescriptionItem,
    DentalRecord, ToothHistory, AmbientScribingNote
)


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'record_type', 'record_date', 'created_at']
    list_filter = ['record_type', 'record_date']
    search_fields = ['patient__user__first_name', 'doctor__user__first_name']
    date_hierarchy = 'record_date'


@admin.register(MedicalFile)
class MedicalFileAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'file_type', 'patient', 'created_at']
    list_filter = ['file_type']
    search_fields = ['file_name', 'patient__user__first_name']


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'prescription_date', 'is_signed']
    list_filter = ['is_signed', 'prescription_date']


@admin.register(PrescriptionItem)
class PrescriptionItemAdmin(admin.ModelAdmin):
    list_display = ['prescription', 'medication_name', 'dosage', 'frequency']


@admin.register(DentalRecord)
class DentalRecordAdmin(admin.ModelAdmin):
    list_display = ['medical_record', 'oral_hygiene_status', 'created_at']


@admin.register(ToothHistory)
class ToothHistoryAdmin(admin.ModelAdmin):
    list_display = ['patient', 'tooth_number', 'procedure', 'procedure_date']
    list_filter = ['procedure']


@admin.register(AmbientScribingNote)
class AmbientScribingNoteAdmin(admin.ModelAdmin):
    list_display = ['medical_record', 'status', 'created_at']
    list_filter = ['status']
