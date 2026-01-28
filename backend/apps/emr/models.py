"""
Electronic Medical Records (EMR) models for HMS.
Includes encrypted notes and dental odontogram support.
"""
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel
from apps.core.encryption import encrypt_field, decrypt_field


class MedicalRecord(BaseModel):
    """
    Main medical record/visit entry.
    """
    RECORD_TYPES = [
        ('consultation', 'Consultation'),
        ('follow_up', 'Follow-up'),
        ('emergency', 'Emergency'),
        ('lab_result', 'Lab Result'),
        ('imaging', 'Imaging'),
        ('procedure', 'Procedure'),
        ('prescription', 'Prescription'),
    ]
    
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='medical_records')
    clinic = models.ForeignKey('clinics.Clinic', on_delete=models.CASCADE, related_name='medical_records')
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='medical_records'
    )
    
    record_type = models.CharField(max_length=20, choices=RECORD_TYPES, default='consultation')
    record_date = models.DateField()
    
    # Chief Complaint
    chief_complaint = models.TextField(blank=True)
    
    # Vitals
    blood_pressure_systolic = models.PositiveIntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.PositiveIntegerField(null=True, blank=True)
    heart_rate = models.PositiveIntegerField(null=True, blank=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    respiratory_rate = models.PositiveIntegerField(null=True, blank=True)
    oxygen_saturation = models.PositiveIntegerField(null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Encrypted Clinical Notes (HIPAA compliant)
    _encrypted_notes = models.TextField(blank=True, db_column='encrypted_notes')
    _encrypted_diagnosis = models.TextField(blank=True, db_column='encrypted_diagnosis')
    _encrypted_treatment_plan = models.TextField(blank=True, db_column='encrypted_treatment_plan')
    
    # ICD codes
    icd_codes = models.JSONField(default=list)  # List of ICD-10 codes
    
    # Follow-up
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'medical_records'
        ordering = ['-record_date', '-created_at']
        indexes = [
            models.Index(fields=['patient', 'record_date']),
            models.Index(fields=['doctor', 'record_date']),
        ]
    
    def __str__(self):
        return f"{self.patient.user.full_name} - {self.record_type} ({self.record_date})"
    
    @property
    def notes(self):
        """Decrypt and return notes."""
        return decrypt_field(self._encrypted_notes) if self._encrypted_notes else ''
    
    @notes.setter
    def notes(self, value):
        """Encrypt and store notes."""
        self._encrypted_notes = encrypt_field(value) if value else ''
    
    @property
    def diagnosis(self):
        """Decrypt and return diagnosis."""
        return decrypt_field(self._encrypted_diagnosis) if self._encrypted_diagnosis else ''
    
    @diagnosis.setter
    def diagnosis(self, value):
        """Encrypt and store diagnosis."""
        self._encrypted_diagnosis = encrypt_field(value) if value else ''
    
    @property
    def treatment_plan(self):
        """Decrypt and return treatment plan."""
        return decrypt_field(self._encrypted_treatment_plan) if self._encrypted_treatment_plan else ''
    
    @treatment_plan.setter
    def treatment_plan(self, value):
        """Encrypt and store treatment plan."""
        self._encrypted_treatment_plan = encrypt_field(value) if value else ''
    
    @property
    def blood_pressure(self):
        """Return formatted blood pressure."""
        if self.blood_pressure_systolic and self.blood_pressure_diastolic:
            return f"{self.blood_pressure_systolic}/{self.blood_pressure_diastolic}"
        return None


class MedicalFile(BaseModel):
    """
    Medical files/attachments (X-rays, lab reports, etc.).
    Stored in S3 with signed URLs.
    """
    FILE_TYPES = [
        ('xray', 'X-Ray'),
        ('mri', 'MRI'),
        ('ct_scan', 'CT Scan'),
        ('ultrasound', 'Ultrasound'),
        ('lab_report', 'Lab Report'),
        ('prescription', 'Prescription'),
        ('photo', 'Clinical Photo'),
        ('document', 'Document'),
        ('other', 'Other'),
    ]
    
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name='files',
        null=True,
        blank=True
    )
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='medical_files')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    file_type = models.CharField(max_length=20, choices=FILE_TYPES, default='document')
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)  # S3 key
    file_size = models.PositiveIntegerField()  # bytes
    mime_type = models.CharField(max_length=100)
    
    description = models.TextField(blank=True)
    
    # Annotations (for image markup)
    annotations = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'medical_files'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.file_name} ({self.file_type})"
    
    def get_signed_url(self, expiration: int = 600):
        """Generate a signed URL for file access (10 min default)."""
        from apps.core.s3_utils import generate_presigned_url
        return generate_presigned_url(self.file_path, expiration)


class Prescription(BaseModel):
    """
    Prescription model for medications.
    """
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name='prescriptions'
    )
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='prescriptions')
    
    prescription_date = models.DateField()
    valid_until = models.DateField(null=True, blank=True)
    
    notes = models.TextField(blank=True)
    
    # Digital signature
    is_signed = models.BooleanField(default=False)
    signed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'prescriptions'
        ordering = ['-prescription_date']
    
    def __str__(self):
        return f"Rx for {self.patient.user.full_name} by Dr. {self.doctor.user.full_name}"


class PrescriptionItem(BaseModel):
    """
    Individual medication in a prescription.
    """
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    
    medication_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)  # e.g., "Twice daily"
    duration = models.CharField(max_length=100)  # e.g., "7 days"
    quantity = models.CharField(max_length=50, blank=True)
    
    instructions = models.TextField(blank=True)  # Before/after food, etc.
    
    class Meta:
        db_table = 'prescription_items'
        ordering = ['id']
    
    def __str__(self):
        return f"{self.medication_name} - {self.dosage}"


class DentalRecord(BaseModel):
    """
    Dental-specific record with tooth-by-tooth tracking.
    """
    medical_record = models.OneToOneField(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name='dental_record'
    )
    
    # Odontogram data - stores status of all 32 teeth
    odontogram = models.JSONField(default=dict)
    
    # Overall dental assessment
    oral_hygiene_status = models.CharField(max_length=50, blank=True)
    gum_condition = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'dental_records'
    
    def __str__(self):
        return f"Dental Record - {self.medical_record}"


class ToothHistory(BaseModel):
    """
    History of treatments for a specific tooth.
    """
    TOOTH_PROCEDURES = [
        ('filling', 'Filling'),
        ('extraction', 'Extraction'),
        ('root_canal', 'Root Canal'),
        ('crown', 'Crown'),
        ('bridge', 'Bridge'),
        ('implant', 'Implant'),
        ('cleaning', 'Cleaning'),
        ('whitening', 'Whitening'),
        ('cavity', 'Cavity Detected'),
        ('other', 'Other'),
    ]
    
    TOOTH_NUMBERS = [(i, str(i)) for i in range(1, 33)]
    
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='tooth_history')
    dental_record = models.ForeignKey(
        DentalRecord,
        on_delete=models.CASCADE,
        related_name='tooth_histories',
        null=True,
        blank=True
    )
    
    tooth_number = models.PositiveIntegerField(choices=TOOTH_NUMBERS)
    procedure = models.CharField(max_length=20, choices=TOOTH_PROCEDURES)
    procedure_date = models.DateField()
    
    notes = models.TextField(blank=True)
    
    # Surface affected (for fillings)
    surface = models.CharField(max_length=50, blank=True)  # e.g., "Mesial", "Occlusal"
    
    class Meta:
        db_table = 'tooth_history'
        ordering = ['-procedure_date']
    
    def __str__(self):
        return f"Tooth #{self.tooth_number} - {self.procedure} ({self.procedure_date})"


class AmbientScribingNote(BaseModel):
    """
    AI-generated notes from ambient scribing during consultations.
    """
    STATUS_CHOICES = [
        ('transcribing', 'Transcribing'),
        ('processing', 'Processing'),
        ('draft', 'Draft'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
    ]
    
    medical_record = models.ForeignKey(
        MedicalRecord,
        on_delete=models.CASCADE,
        related_name='scribing_notes'
    )
    
    # Audio file reference
    audio_file_path = models.CharField(max_length=500, blank=True)
    audio_duration = models.PositiveIntegerField(null=True, blank=True)  # seconds
    
    # Transcription
    raw_transcription = models.TextField(blank=True)
    
    # AI-generated structured note
    ai_generated_note = models.TextField(blank=True)
    
    # Doctor's reviewed/edited version
    final_note = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='transcribing')
    
    reviewed_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'ambient_scribing_notes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Scribing Note - {self.medical_record} ({self.status})"
