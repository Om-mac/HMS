"""
Serializers for patient management.
"""
from rest_framework import serializers
from .models import Patient, PatientAllergy, PatientMedication, PatientChronicCondition, Waitlist
from apps.users.serializers import UserSerializer


class PatientAllergySerializer(serializers.ModelSerializer):
    """Serializer for patient allergies."""
    
    class Meta:
        model = PatientAllergy
        fields = ['id', 'allergen', 'reaction', 'severity', 'diagnosed_date', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class PatientMedicationSerializer(serializers.ModelSerializer):
    """Serializer for patient medications."""
    
    class Meta:
        model = PatientMedication
        fields = [
            'id', 'medication_name', 'dosage', 'frequency', 'start_date',
            'end_date', 'prescribing_doctor', 'purpose', 'notes', 'is_current', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PatientChronicConditionSerializer(serializers.ModelSerializer):
    """Serializer for patient chronic conditions."""
    
    class Meta:
        model = PatientChronicCondition
        fields = ['id', 'condition_name', 'icd_code', 'diagnosed_date', 'status', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class PatientSerializer(serializers.ModelSerializer):
    """Serializer for patient profile."""
    
    user = UserSerializer(read_only=True)
    allergies = PatientAllergySerializer(many=True, read_only=True)
    medications = PatientMedicationSerializer(many=True, read_only=True)
    chronic_conditions = PatientChronicConditionSerializer(many=True, read_only=True)
    qr_code = serializers.SerializerMethodField()
    bmi = serializers.ReadOnlyField()
    
    class Meta:
        model = Patient
        fields = [
            'id', 'user', 'patient_id', 'blood_type', 'gender', 'height_cm',
            'weight_kg', 'bmi', 'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relation', 'insurance_provider', 'insurance_policy_number',
            'insurance_expiry', 'preferred_language', 'occupation', 'allergies',
            'medications', 'chronic_conditions', 'qr_code', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'patient_id', 'qr_code', 'created_at', 'updated_at']
    
    def get_qr_code(self, obj):
        return obj.get_qr_code()


class PatientCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating patient profile."""
    
    class Meta:
        model = Patient
        fields = [
            'blood_type', 'gender', 'height_cm', 'weight_kg',
            'emergency_contact_name', 'emergency_contact_phone',
            'emergency_contact_relation', 'insurance_provider',
            'insurance_policy_number', 'insurance_expiry',
            'preferred_language', 'occupation'
        ]


class PatientListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for patient lists."""
    
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    
    class Meta:
        model = Patient
        fields = ['id', 'patient_id', 'full_name', 'email', 'phone_number', 'gender', 'blood_type']


class WaitlistSerializer(serializers.ModelSerializer):
    """Serializer for waitlist entries."""
    
    patient_name = serializers.CharField(source='patient.user.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.full_name', read_only=True)
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    
    class Meta:
        model = Waitlist
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'clinic', 'clinic_name', 'preferred_date', 'preferred_time_start',
            'preferred_time_end', 'reason', 'status', 'notification_sent_at',
            'created_at'
        ]
        read_only_fields = ['id', 'notification_sent_at', 'created_at']
