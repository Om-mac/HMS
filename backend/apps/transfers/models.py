"""
Federated Patient Transfer models.
Implements the "Handshake" system for secure inter-hospital data sharing.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from apps.core.models import BaseModel
import secrets


class PatientAccess(BaseModel):
    """
    Tracks which doctors have access to which patients' records.
    Access is granted, not data copied (federated approach).
    """
    ACCESS_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('revoked', 'Revoked'),
        ('expired', 'Expired'),
    ]
    
    ACCESS_LEVELS = [
        ('full', 'Full Access'),
        ('summary', 'Summary Only'),
        ('specific', 'Specific Records'),
    ]
    
    # The doctor requesting access
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='patient_accesses')
    
    # The patient whose records are being accessed
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='access_grants')
    
    # The doctor who grants access (patient's primary/treating doctor)
    granted_by = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='access_grants_given'
    )
    
    # Or patient can grant access directly
    patient_granted = models.BooleanField(default=False)
    
    status = models.CharField(max_length=20, choices=ACCESS_STATUS, default='pending')
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVELS, default='full')
    
    # Specific records if access_level is 'specific'
    specific_record_ids = models.JSONField(default=list, blank=True)
    
    # Request details
    reason = models.TextField()
    
    # Access validity
    requested_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    
    # Rejection/Revocation reason
    rejection_reason = models.TextField(blank=True)
    
    class Meta:
        db_table = 'patient_access'
        ordering = ['-requested_at']
        unique_together = ['doctor', 'patient', 'status']
    
    def __str__(self):
        return f"Dr. {self.doctor.user.full_name} -> {self.patient.user.full_name} ({self.status})"
    
    def approve(self, granted_by=None, valid_days=30):
        """Approve access request."""
        self.status = 'approved'
        self.granted_by = granted_by
        self.responded_at = timezone.now()
        self.valid_from = timezone.now()
        self.valid_until = timezone.now() + timedelta(days=valid_days)
        self.save()
        
        # Create permission token
        return PermissionToken.create_for_access(self)
    
    def reject(self, reason=''):
        """Reject access request."""
        self.status = 'rejected'
        self.responded_at = timezone.now()
        self.rejection_reason = reason
        self.save()
    
    def revoke(self, reason=''):
        """Revoke previously granted access."""
        self.status = 'revoked'
        self.rejection_reason = reason
        self.save()
        
        # Invalidate any active tokens
        PermissionToken.objects.filter(access=self).update(is_revoked=True)
    
    @property
    def is_valid(self):
        """Check if access is currently valid."""
        if self.status != 'approved':
            return False
        if self.valid_until and timezone.now() > self.valid_until:
            return False
        return True


class PermissionToken(BaseModel):
    """
    Temporary permission token for accessing patient data.
    Acts as a time-limited key for federated access.
    """
    access = models.ForeignKey(PatientAccess, on_delete=models.CASCADE, related_name='tokens')
    
    token = models.CharField(max_length=64, unique=True)
    
    valid_until = models.DateTimeField()
    is_revoked = models.BooleanField(default=False)
    
    # Usage tracking
    times_used = models.PositiveIntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'permission_tokens'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Token for {self.access}"
    
    @classmethod
    def create_for_access(cls, access: PatientAccess, valid_hours: int = 24):
        """Create a new permission token for access grant."""
        return cls.objects.create(
            access=access,
            token=secrets.token_urlsafe(48),
            valid_until=timezone.now() + timedelta(hours=valid_hours)
        )
    
    @property
    def is_valid(self):
        """Check if token is currently valid."""
        if self.is_revoked:
            return False
        if timezone.now() > self.valid_until:
            return False
        if not self.access.is_valid:
            return False
        return True
    
    def use(self):
        """Record token usage."""
        self.times_used += 1
        self.last_used_at = timezone.now()
        self.save(update_fields=['times_used', 'last_used_at'])


class TransferRequest(BaseModel):
    """
    Formal request for patient data transfer between facilities.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    TRANSFER_TYPES = [
        ('referral', 'Referral'),
        ('second_opinion', 'Second Opinion'),
        ('specialist', 'Specialist Consultation'),
        ('emergency', 'Emergency Transfer'),
        ('continuation', 'Care Continuation'),
    ]
    
    # Request details
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='transfer_requests')
    
    # From (requesting facility/doctor)
    requesting_doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        related_name='transfer_requests_made'
    )
    requesting_clinic = models.ForeignKey(
        'clinics.Clinic',
        on_delete=models.CASCADE,
        related_name='transfer_requests_from'
    )
    
    # To (receiving facility/doctor)
    receiving_doctor = models.ForeignKey(
        'doctors.Doctor',
        on_delete=models.CASCADE,
        related_name='transfer_requests_received',
        null=True,
        blank=True
    )
    receiving_clinic = models.ForeignKey(
        'clinics.Clinic',
        on_delete=models.CASCADE,
        related_name='transfer_requests_to'
    )
    
    transfer_type = models.CharField(max_length=20, choices=TRANSFER_TYPES, default='referral')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Clinical details
    reason = models.TextField()
    clinical_summary = models.TextField(blank=True)
    urgency = models.CharField(max_length=20, default='routine', choices=[
        ('routine', 'Routine'),
        ('urgent', 'Urgent'),
        ('emergency', 'Emergency'),
    ])
    
    # Response
    response_notes = models.TextField(blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    responded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transfer_responses'
    )
    
    # Completion
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'transfer_requests'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Transfer: {self.patient.user.full_name} ({self.status})"
    
    def approve(self, responded_by, notes=''):
        """Approve transfer request and create access grant."""
        self.status = 'approved'
        self.responded_by = responded_by
        self.responded_at = timezone.now()
        self.response_notes = notes
        self.save()
        
        # Create patient access for the receiving doctor
        if self.receiving_doctor:
            PatientAccess.objects.create(
                doctor=self.receiving_doctor,
                patient=self.patient,
                granted_by=self.requesting_doctor,
                status='approved',
                reason=f"Transfer request: {self.reason}",
                valid_from=timezone.now(),
                valid_until=timezone.now() + timedelta(days=90)
            )
    
    def reject(self, responded_by, reason=''):
        """Reject transfer request."""
        self.status = 'rejected'
        self.responded_by = responded_by
        self.responded_at = timezone.now()
        self.response_notes = reason
        self.save()
