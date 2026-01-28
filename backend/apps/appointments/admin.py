from django.contrib import admin
from .models import Appointment, AppointmentHistory, LiveQueue


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['get_patient', 'get_doctor', 'appointment_date', 'start_time', 'status', 'token_number']
    list_filter = ['status', 'appointment_type', 'appointment_date']
    search_fields = ['patient__user__first_name', 'doctor__user__first_name']
    date_hierarchy = 'appointment_date'
    
    def get_patient(self, obj):
        return obj.patient.user.full_name
    get_patient.short_description = 'Patient'
    
    def get_doctor(self, obj):
        return f"Dr. {obj.doctor.user.full_name}"
    get_doctor.short_description = 'Doctor'


@admin.register(AppointmentHistory)
class AppointmentHistoryAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'previous_status', 'new_status', 'changed_by', 'created_at']
    list_filter = ['new_status', 'created_at']


@admin.register(LiveQueue)
class LiveQueueAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'queue_position', 'status', 'called_at']
    list_filter = ['status']
