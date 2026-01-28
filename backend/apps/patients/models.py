"""
Patient models for HMS.
"""
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel
from apps.core.qr_utils import generate_qr_base64


class Patient(BaseModel):
    """
    Patient profile model with unique QR-ID for universal identification.
    """
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_profile'
    )
    
    # Unique Patient Identifier
    patient_id = models.CharField(max_length=20, unique=True, editable=False)
    
    # Medical Information
    blood_type = models.CharField(max_length=5, choices=BLOOD_TYPE_CHOICES, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True)
    
    # Insurance
    insurance_provider = models.CharField(max_length=200, blank=True)
    insurance_policy_number = models.CharField(max_length=100, blank=True)
    insurance_expiry = models.DateField(null=True, blank=True)
    
    # Preferences
    preferred_language = models.CharField(max_length=50, default='English')
    
    # Additional fields
    occupation = models.CharField(max_length=200, blank=True)
    
    class Meta:
        db_table = 'patients'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.full_name} ({self.patient_id})"
    
    def save(self, *args, **kwargs):
        if not self.patient_id:
            self.patient_id = self._generate_patient_id()
        super().save(*args, **kwargs)
    
    def _generate_patient_id(self):
        """Generate a unique patient ID."""
        import random
        import string
        prefix = 'PT'
        random_part = ''.join(random.choices(string.digits, k=8))
        return f"{prefix}{random_part}"
    
    def get_qr_code(self):
        """Generate QR code for this patient."""
        return generate_qr_base64(str(self.id), self.user.full_name)
    
    @property
    def bmi(self):
        """Calculate BMI if height and weight are available."""
        if self.height_cm and self.weight_kg:
            height_m = float(self.height_cm) / 100
            return round(float(self.weight_kg) / (height_m ** 2), 1)
        return None


class PatientAllergy(BaseModel):
    """
    Patient allergies tracking.
    """
    SEVERITY_CHOICES = [
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
        ('life_threatening', 'Life Threatening'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='allergies')
    allergen = models.CharField(max_length=200)
    reaction = models.TextField(blank=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='moderate')
    diagnosed_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'patient_allergies'
        ordering = ['-severity', 'allergen']
        unique_together = ['patient', 'allergen']
    
    def __str__(self):
        return f"{self.patient.user.full_name} - {self.allergen}"


class PatientMedication(BaseModel):
    """
    Current medications for a patient.
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medications')
    medication_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    prescribing_doctor = models.CharField(max_length=200, blank=True)
    purpose = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    is_current = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'patient_medications'
        ordering = ['-is_current', '-start_date']
    
    def __str__(self):
        return f"{self.patient.user.full_name} - {self.medication_name}"


class PatientChronicCondition(BaseModel):
    """
    Chronic conditions/diseases for a patient.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('controlled', 'Controlled'),
        ('in_remission', 'In Remission'),
        ('resolved', 'Resolved'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='chronic_conditions')
    condition_name = models.CharField(max_length=200)
    icd_code = models.CharField(max_length=20, blank=True)  # ICD-10 code
    diagnosed_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'patient_chronic_conditions'
        ordering = ['-status', 'condition_name']
    
    def __str__(self):
        return f"{self.patient.user.full_name} - {self.condition_name}"


class Waitlist(BaseModel):
    """
    Waitlist for appointment slots.
    """
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('notified', 'Notified'),
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='waitlist_entries')
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='waitlist_entries')
    clinic = models.ForeignKey('clinics.Clinic', on_delete=models.CASCADE, related_name='waitlist_entries')
    
    preferred_date = models.DateField()
    preferred_time_start = models.TimeField(null=True, blank=True)
    preferred_time_end = models.TimeField(null=True, blank=True)
    reason = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    notification_sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'patient_waitlist'
        ordering = ['preferred_date', 'created_at']
    
    def __str__(self):
        return f"{self.patient.user.full_name} - Waitlist for Dr. {self.doctor.user.full_name}"
