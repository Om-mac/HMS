"""
Serializers for patient transfers.
"""
from rest_framework import serializers
from .models import PatientAccess, PermissionToken, TransferRequest


class PermissionTokenSerializer(serializers.ModelSerializer):
    """Serializer for permission tokens."""
    
    class Meta:
        model = PermissionToken
        fields = ['id', 'token', 'valid_until', 'is_revoked', 'times_used', 'last_used_at', 'created_at']
        read_only_fields = ['token', 'created_at']


class PatientAccessSerializer(serializers.ModelSerializer):
    """Serializer for patient access grants."""
    
    doctor_name = serializers.CharField(source='doctor.user.full_name', read_only=True)
    patient_name = serializers.CharField(source='patient.user.full_name', read_only=True)
    patient_id = serializers.CharField(source='patient.patient_id', read_only=True)
    granted_by_name = serializers.CharField(source='granted_by.user.full_name', read_only=True)
    is_valid = serializers.ReadOnlyField()
    tokens = PermissionTokenSerializer(many=True, read_only=True)
    
    class Meta:
        model = PatientAccess
        fields = [
            'id', 'doctor', 'doctor_name', 'patient', 'patient_name', 'patient_id',
            'granted_by', 'granted_by_name', 'patient_granted', 'status',
            'access_level', 'specific_record_ids', 'reason', 'requested_at',
            'responded_at', 'valid_from', 'valid_until', 'rejection_reason',
            'is_valid', 'tokens'
        ]
        read_only_fields = ['id', 'requested_at', 'responded_at']


class PatientAccessRequestSerializer(serializers.ModelSerializer):
    """Serializer for requesting patient access."""
    
    class Meta:
        model = PatientAccess
        fields = ['patient', 'access_level', 'specific_record_ids', 'reason']


class PatientAccessResponseSerializer(serializers.Serializer):
    """Serializer for responding to access requests."""
    
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    reason = serializers.CharField(required=False, allow_blank=True)
    valid_days = serializers.IntegerField(default=30, min_value=1, max_value=365)


class TransferRequestSerializer(serializers.ModelSerializer):
    """Serializer for transfer requests."""
    
    patient_name = serializers.CharField(source='patient.user.full_name', read_only=True)
    requesting_doctor_name = serializers.CharField(source='requesting_doctor.user.full_name', read_only=True)
    requesting_clinic_name = serializers.CharField(source='requesting_clinic.name', read_only=True)
    receiving_doctor_name = serializers.CharField(source='receiving_doctor.user.full_name', read_only=True)
    receiving_clinic_name = serializers.CharField(source='receiving_clinic.name', read_only=True)
    
    class Meta:
        model = TransferRequest
        fields = [
            'id', 'patient', 'patient_name', 'requesting_doctor', 'requesting_doctor_name',
            'requesting_clinic', 'requesting_clinic_name', 'receiving_doctor',
            'receiving_doctor_name', 'receiving_clinic', 'receiving_clinic_name',
            'transfer_type', 'status', 'reason', 'clinical_summary', 'urgency',
            'response_notes', 'responded_at', 'completed_at', 'created_at'
        ]
        read_only_fields = ['id', 'responded_at', 'completed_at', 'created_at']


class TransferRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating transfer requests."""
    
    class Meta:
        model = TransferRequest
        fields = [
            'patient', 'receiving_doctor', 'receiving_clinic',
            'transfer_type', 'reason', 'clinical_summary', 'urgency'
        ]


class TransferResponseSerializer(serializers.Serializer):
    """Serializer for responding to transfer requests."""
    
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    notes = serializers.CharField(required=False, allow_blank=True)
