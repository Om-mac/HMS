"""
Doctor models for HMS.
"""
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel


class Specialization(BaseModel):
    """Medical specializations."""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # Icon class name
    
    class Meta:
        db_table = 'specializations'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Doctor(BaseModel):
    """
    Doctor profile model.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile'
    )
    
    # Professional Information
    registration_number = models.CharField(max_length=50, unique=True)
    specializations = models.ManyToManyField(Specialization, related_name='doctors')
    qualification = models.CharField(max_length=500)
    experience_years = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True)
    
    # Consultation
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    consultation_duration = models.PositiveIntegerField(default=30)  # minutes
    
    # Clinic affiliations
    clinics = models.ManyToManyField('clinics.Clinic', through='DoctorClinic', related_name='doctors')
    
    # Ratings
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    
    # Availability
    is_accepting_patients = models.BooleanField(default=True)
    
    # Signature for prescriptions
    digital_signature = models.ImageField(upload_to='doctor_signatures/', null=True, blank=True)
    
    class Meta:
        db_table = 'doctors'
        ordering = ['-average_rating', 'user__first_name']
    
    def __str__(self):
        return f"Dr. {self.user.full_name}"
    
    @property
    def specialization_list(self):
        return list(self.specializations.values_list('name', flat=True))


class DoctorClinic(BaseModel):
    """
    Association between doctors and clinics with schedule information.
    """
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='doctor_clinics')
    clinic = models.ForeignKey('clinics.Clinic', on_delete=models.CASCADE, related_name='clinic_doctors')
    
    # Consultation fee at this clinic (may differ from default)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Status
    is_primary = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'doctor_clinics'
        unique_together = ['doctor', 'clinic']
    
    def __str__(self):
        return f"Dr. {self.doctor.user.full_name} at {self.clinic.name}"


class DoctorSchedule(BaseModel):
    """
    Doctor's working schedule at a specific clinic.
    """
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    doctor_clinic = models.ForeignKey(DoctorClinic, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Break time
    break_start = models.TimeField(null=True, blank=True)
    break_end = models.TimeField(null=True, blank=True)
    
    # Slot configuration
    slot_duration = models.PositiveIntegerField(default=30)  # minutes
    max_patients = models.PositiveIntegerField(default=20)
    
    class Meta:
        db_table = 'doctor_schedules'
        ordering = ['day_of_week', 'start_time']
        unique_together = ['doctor_clinic', 'day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.doctor_clinic.doctor.user.full_name} - {self.get_day_of_week_display()}"


class DoctorLeave(BaseModel):
    """
    Doctor's leave/unavailability periods.
    """
    LEAVE_TYPES = [
        ('vacation', 'Vacation'),
        ('sick', 'Sick Leave'),
        ('conference', 'Conference'),
        ('emergency', 'Emergency'),
        ('other', 'Other'),
    ]
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='leaves')
    clinic = models.ForeignKey('clinics.Clinic', on_delete=models.CASCADE, null=True, blank=True)
    
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES, default='vacation')
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)  # For partial day leave
    end_time = models.TimeField(null=True, blank=True)
    reason = models.TextField(blank=True)
    
    class Meta:
        db_table = 'doctor_leaves'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"Dr. {self.doctor.user.full_name} - {self.start_date} to {self.end_date}"
