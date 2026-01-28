from django.contrib import admin
from .models import Patient, PatientAllergy, PatientMedication, PatientChronicCondition, Waitlist


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_id', 'get_full_name', 'blood_type', 'gender', 'created_at']
    list_filter = ['blood_type', 'gender', 'is_active']
    search_fields = ['patient_id', 'user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['patient_id', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.user.full_name
    get_full_name.short_description = 'Name'


@admin.register(PatientAllergy)
class PatientAllergyAdmin(admin.ModelAdmin):
    list_display = ['patient', 'allergen', 'severity', 'created_at']
    list_filter = ['severity']
    search_fields = ['patient__user__first_name', 'allergen']


@admin.register(PatientMedication)
class PatientMedicationAdmin(admin.ModelAdmin):
    list_display = ['patient', 'medication_name', 'dosage', 'is_current', 'start_date']
    list_filter = ['is_current']
    search_fields = ['patient__user__first_name', 'medication_name']


@admin.register(PatientChronicCondition)
class PatientChronicConditionAdmin(admin.ModelAdmin):
    list_display = ['patient', 'condition_name', 'status', 'diagnosed_date']
    list_filter = ['status']
    search_fields = ['patient__user__first_name', 'condition_name']


@admin.register(Waitlist)
class WaitlistAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'preferred_date', 'status', 'created_at']
    list_filter = ['status', 'preferred_date']
    search_fields = ['patient__user__first_name', 'doctor__user__first_name']
