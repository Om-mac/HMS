"""
Appointment models for HMS.
"""
from django.db import models
from django.conf import settings
from apps.core.models import BaseModel


class Appointment(BaseModel):
    """
    Appointment model for scheduling consultations.
    """
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('rescheduled', 'Rescheduled'),
        ('checked_in', 'Checked In'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    APPOINTMENT_TYPES = [
        ('new', 'New Consultation'),
        ('follow_up', 'Follow-up'),
        ('routine', 'Routine Check-up'),
        ('emergency', 'Emergency'),
        ('teleconsultation', 'Teleconsultation'),
    ]
    
    # Relationships
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='appointments')
    clinic = models.ForeignKey('clinics.Clinic', on_delete=models.CASCADE, related_name='appointments')
    
    # Appointment Details
    appointment_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    appointment_type = models.CharField(max_length=20, choices=APPOINTMENT_TYPES, default='new')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Reason/Notes
    reason = models.TextField(blank=True)
    patient_notes = models.TextField(blank=True)
    doctor_notes = models.TextField(blank=True)
    
    # Fee
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('waived', 'Waived'),
        ('refunded', 'Refunded'),
    ])
    
    # Rescheduling
    original_date = models.DateField(null=True, blank=True)
    original_time = models.TimeField(null=True, blank=True)
    reschedule_reason = models.TextField(blank=True)
    rescheduled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rescheduled_appointments'
    )
    
    # Check-in
    checked_in_at = models.DateTimeField(null=True, blank=True)
    
    # Token/Queue
    token_number = models.PositiveIntegerField(null=True, blank=True)
    
    # Reminders
    reminder_sent = models.BooleanField(default=False)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'appointments'
        ordering = ['appointment_date', 'start_time']
        indexes = [
            models.Index(fields=['appointment_date', 'doctor']),
            models.Index(fields=['patient', 'status']),
            models.Index(fields=['status', 'appointment_date']),
        ]
    
    def __str__(self):
        return f"{self.patient.user.full_name} - Dr. {self.doctor.user.full_name} ({self.appointment_date})"
    
    def save(self, *args, **kwargs):
        # Set consultation fee from doctor if not set
        if not self.consultation_fee:
            from apps.doctors.models import DoctorClinic
            try:
                dc = DoctorClinic.objects.get(doctor=self.doctor, clinic=self.clinic)
                self.consultation_fee = dc.consultation_fee or self.doctor.consultation_fee
            except DoctorClinic.DoesNotExist:
                self.consultation_fee = self.doctor.consultation_fee
        
        # Generate token number
        if not self.token_number and self.status in ['scheduled', 'confirmed']:
            self.token_number = self._generate_token()
        
        super().save(*args, **kwargs)
    
    def _generate_token(self):
        """Generate daily token number for the clinic."""
        today_appointments = Appointment.objects.filter(
            clinic=self.clinic,
            appointment_date=self.appointment_date,
            token_number__isnull=False
        ).exclude(id=self.id)
        
        max_token = today_appointments.aggregate(models.Max('token_number'))['token_number__max']
        return (max_token or 0) + 1


class AppointmentHistory(BaseModel):
    """
    Track all status changes for appointments.
    """
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='history')
    previous_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'appointment_history'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.appointment} - {self.previous_status} -> {self.new_status}"


class LiveQueue(BaseModel):
    """
    Real-time queue management for appointments.
    """
    QUEUE_STATUS = [
        ('waiting', 'Waiting'),
        ('called', 'Called'),
        ('with_doctor', 'With Doctor'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ]
    
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='queue_entry')
    clinic = models.ForeignKey('clinics.Clinic', on_delete=models.CASCADE, related_name='queue_entries')
    doctor = models.ForeignKey('doctors.Doctor', on_delete=models.CASCADE, related_name='queue_entries')
    
    queue_position = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=QUEUE_STATUS, default='waiting')
    
    called_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    estimated_wait_time = models.PositiveIntegerField(null=True, blank=True)  # minutes
    
    class Meta:
        db_table = 'live_queue'
        ordering = ['queue_position']
    
    def __str__(self):
        return f"Queue #{self.queue_position} - {self.appointment.patient.user.full_name}"
