"""
Clinic models for HMS.
"""
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel


class Clinic(BaseModel):
    """
    Clinic/Hospital model.
    """
    CLINIC_TYPES = [
        ('hospital', 'Hospital'),
        ('clinic', 'Clinic'),
        ('diagnostic', 'Diagnostic Center'),
        ('dental', 'Dental Clinic'),
        ('eye', 'Eye Clinic'),
        ('specialty', 'Specialty Center'),
    ]
    
    name = models.CharField(max_length=300)
    clinic_type = models.CharField(max_length=20, choices=CLINIC_TYPES, default='clinic')
    registration_number = models.CharField(max_length=100, unique=True)
    
    # Contact
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    postal_code = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    
    # Operating Hours
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    
    # Facilities
    has_pharmacy = models.BooleanField(default=False)
    has_lab = models.BooleanField(default=False)
    has_emergency = models.BooleanField(default=False)
    has_ambulance = models.BooleanField(default=False)
    
    # Media
    logo = models.ImageField(upload_to='clinic_logos/', null=True, blank=True)
    
    # Admin
    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='administered_clinics'
    )
    
    # Ratings
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'clinics'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ClinicFacility(BaseModel):
    """
    Facilities available at a clinic.
    """
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='facilities')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'clinic_facilities'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.clinic.name} - {self.name}"


class ClinicHoliday(BaseModel):
    """
    Holidays/closures for a clinic.
    """
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='holidays')
    date = models.DateField()
    reason = models.CharField(max_length=200)
    
    class Meta:
        db_table = 'clinic_holidays'
        ordering = ['date']
        unique_together = ['clinic', 'date']
    
    def __str__(self):
        return f"{self.clinic.name} - {self.date}"
