from django.contrib import admin
from .models import Doctor, Specialization, DoctorClinic, DoctorSchedule, DoctorLeave


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active']
    search_fields = ['name']


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'registration_number', 'experience_years', 'average_rating', 'is_accepting_patients']
    list_filter = ['is_accepting_patients', 'specializations']
    search_fields = ['user__first_name', 'user__last_name', 'registration_number']
    filter_horizontal = ['specializations']
    
    def get_full_name(self, obj):
        return f"Dr. {obj.user.full_name}"
    get_full_name.short_description = 'Name'


@admin.register(DoctorClinic)
class DoctorClinicAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'clinic', 'consultation_fee', 'is_primary', 'is_active']
    list_filter = ['is_primary', 'is_active']


@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ['doctor_clinic', 'day_of_week', 'start_time', 'end_time', 'slot_duration']
    list_filter = ['day_of_week']


@admin.register(DoctorLeave)
class DoctorLeaveAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'leave_type', 'start_date', 'end_date']
    list_filter = ['leave_type', 'start_date']
