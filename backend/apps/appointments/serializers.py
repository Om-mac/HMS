"""
Serializers for appointment management.
"""
from rest_framework import serializers
from .models import Appointment, AppointmentHistory, LiveQueue
from apps.patients.serializers import PatientListSerializer
from apps.doctors.serializers import DoctorListSerializer


class AppointmentHistorySerializer(serializers.ModelSerializer):
    """Serializer for appointment history."""
    changed_by_name = serializers.CharField(source='changed_by.full_name', read_only=True)
    
    class Meta:
        model = AppointmentHistory
        fields = ['id', 'previous_status', 'new_status', 'changed_by', 'changed_by_name', 'notes', 'created_at']


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for appointment details."""
    
    patient_name = serializers.CharField(source='patient.user.full_name', read_only=True)
    patient_phone = serializers.CharField(source='patient.user.phone_number', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.full_name', read_only=True)
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    clinic_address = serializers.CharField(source='clinic.address', read_only=True)
    history = AppointmentHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'patient_phone', 'doctor', 'doctor_name',
            'clinic', 'clinic_name', 'clinic_address', 'appointment_date', 'start_time',
            'end_time', 'appointment_type', 'status', 'reason', 'patient_notes',
            'doctor_notes', 'consultation_fee', 'payment_status', 'original_date',
            'original_time', 'reschedule_reason', 'checked_in_at', 'token_number',
            'reminder_sent', 'history', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'token_number', 'checked_in_at', 'reminder_sent',
            'created_at', 'updated_at'
        ]


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating appointments."""
    
    class Meta:
        model = Appointment
        fields = [
            'patient', 'doctor', 'clinic', 'appointment_date', 'start_time',
            'end_time', 'appointment_type', 'reason', 'patient_notes'
        ]
    
    def validate(self, attrs):
        # Validate appointment time is available
        from datetime import datetime, timedelta
        
        doctor = attrs['doctor']
        clinic = attrs['clinic']
        date = attrs['appointment_date']
        start_time = attrs['start_time']
        
        # Check for existing appointments
        existing = Appointment.objects.filter(
            doctor=doctor,
            clinic=clinic,
            appointment_date=date,
            start_time=start_time,
            status__in=['scheduled', 'confirmed', 'checked_in']
        )
        
        if existing.exists():
            raise serializers.ValidationError({
                'start_time': 'This time slot is already booked.'
            })
        
        # Check if doctor has leave
        from apps.doctors.models import DoctorLeave
        leaves = DoctorLeave.objects.filter(
            doctor=doctor,
            start_date__lte=date,
            end_date__gte=date
        )
        if leaves.exists():
            raise serializers.ValidationError({
                'appointment_date': 'Doctor is not available on this date.'
            })
        
        return attrs


class AppointmentRescheduleSerializer(serializers.Serializer):
    """Serializer for rescheduling appointments."""
    
    new_date = serializers.DateField()
    new_start_time = serializers.TimeField()
    new_end_time = serializers.TimeField()
    reason = serializers.CharField(required=False, allow_blank=True)


class AppointmentStatusSerializer(serializers.Serializer):
    """Serializer for updating appointment status."""
    
    status = serializers.ChoiceField(choices=Appointment.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)


class AppointmentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for appointment lists."""
    
    patient_name = serializers.CharField(source='patient.user.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.full_name', read_only=True)
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'patient_name', 'doctor_name', 'clinic_name',
            'appointment_date', 'start_time', 'appointment_type',
            'status', 'token_number'
        ]


class LiveQueueSerializer(serializers.ModelSerializer):
    """Serializer for live queue."""
    
    patient_name = serializers.CharField(source='appointment.patient.user.full_name', read_only=True)
    appointment_type = serializers.CharField(source='appointment.appointment_type', read_only=True)
    token_number = serializers.IntegerField(source='appointment.token_number', read_only=True)
    start_time = serializers.TimeField(source='appointment.start_time', read_only=True)
    
    class Meta:
        model = LiveQueue
        fields = [
            'id', 'queue_position', 'patient_name', 'appointment_type',
            'token_number', 'start_time', 'status', 'estimated_wait_time',
            'called_at', 'started_at', 'completed_at'
        ]


class DoctorDashboardStatsSerializer(serializers.Serializer):
    """Serializer for doctor dashboard statistics."""
    
    total_today = serializers.IntegerField()
    checked_in = serializers.IntegerField()
    in_progress = serializers.IntegerField()
    completed = serializers.IntegerField()
    pending = serializers.IntegerField()
    cancelled = serializers.IntegerField()
    no_show = serializers.IntegerField()
    average_consultation_time = serializers.FloatField()
