from django.contrib import admin
from .models import Clinic, ClinicFacility, ClinicHoliday


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ['name', 'clinic_type', 'city', 'phone', 'has_emergency', 'average_rating']
    list_filter = ['clinic_type', 'city', 'has_emergency', 'has_pharmacy', 'has_lab']
    search_fields = ['name', 'city', 'address']


@admin.register(ClinicFacility)
class ClinicFacilityAdmin(admin.ModelAdmin):
    list_display = ['clinic', 'name', 'is_available']
    list_filter = ['is_available']


@admin.register(ClinicHoliday)
class ClinicHolidayAdmin(admin.ModelAdmin):
    list_display = ['clinic', 'date', 'reason']
    list_filter = ['date']
