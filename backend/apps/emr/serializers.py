"""
Serializers for EMR.
"""
from rest_framework import serializers
from .models import (
    MedicalRecord, MedicalFile, Prescription, PrescriptionItem,
    DentalRecord, ToothHistory, AmbientScribingNote
)


class MedicalFileSerializer(serializers.ModelSerializer):
    """Serializer for medical files."""
    
    signed_url = serializers.SerializerMethodField()
    
    class Meta:
        model = MedicalFile
        fields = [
            'id', 'file_type', 'file_name', 'file_size', 'mime_type',
            'description', 'annotations', 'signed_url', 'created_at'
        ]
        read_only_fields = ['id', 'signed_url', 'created_at']
    
    def get_signed_url(self, obj):
        return obj.get_signed_url()


class PrescriptionItemSerializer(serializers.ModelSerializer):
    """Serializer for prescription items."""
    
    class Meta:
        model = PrescriptionItem
        fields = [
            'id', 'medication_name', 'dosage', 'frequency',
            'duration', 'quantity', 'instructions'
        ]


class PrescriptionSerializer(serializers.ModelSerializer):
    """Serializer for prescriptions."""
    
    items = PrescriptionItemSerializer(many=True, read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.full_name', read_only=True)
    
    class Meta:
        model = Prescription
        fields = [
            'id', 'prescription_date', 'valid_until', 'notes',
            'is_signed', 'signed_at', 'doctor_name', 'items', 'created_at'
        ]
        read_only_fields = ['id', 'is_signed', 'signed_at', 'created_at']


class ToothHistorySerializer(serializers.ModelSerializer):
    """Serializer for tooth history."""
    
    class Meta:
        model = ToothHistory
        fields = [
            'id', 'tooth_number', 'procedure', 'procedure_date',
            'notes', 'surface', 'created_at'
        ]


class DentalRecordSerializer(serializers.ModelSerializer):
    """Serializer for dental records."""
    
    tooth_histories = ToothHistorySerializer(many=True, read_only=True)
    
    class Meta:
        model = DentalRecord
        fields = [
            'id', 'odontogram', 'oral_hygiene_status', 'gum_condition',
            'tooth_histories', 'created_at'
        ]


class AmbientScribingNoteSerializer(serializers.ModelSerializer):
    """Serializer for ambient scribing notes."""
    
    class Meta:
        model = AmbientScribingNote
        fields = [
            'id', 'audio_duration', 'raw_transcription', 'ai_generated_note',
            'final_note', 'status', 'reviewed_at', 'approved_at', 'created_at'
        ]
        read_only_fields = ['id', 'raw_transcription', 'ai_generated_note', 'created_at']


class MedicalRecordSerializer(serializers.ModelSerializer):
    """Serializer for medical records."""
    
    files = MedicalFileSerializer(many=True, read_only=True)
    prescriptions = PrescriptionSerializer(many=True, read_only=True)
    dental_record = DentalRecordSerializer(read_only=True)
    scribing_notes = AmbientScribingNoteSerializer(many=True, read_only=True)
    
    doctor_name = serializers.CharField(source='doctor.user.full_name', read_only=True)
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    blood_pressure = serializers.ReadOnlyField()
    
    # Decrypted fields
    notes = serializers.CharField(required=False, allow_blank=True)
    diagnosis = serializers.CharField(required=False, allow_blank=True)
    treatment_plan = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'patient', 'doctor', 'doctor_name', 'clinic', 'clinic_name',
            'appointment', 'record_type', 'record_date', 'chief_complaint',
            'blood_pressure_systolic', 'blood_pressure_diastolic', 'blood_pressure',
            'heart_rate', 'temperature', 'respiratory_rate', 'oxygen_saturation',
            'weight', 'height', 'notes', 'diagnosis', 'treatment_plan',
            'icd_codes', 'follow_up_required', 'follow_up_date', 'follow_up_notes',
            'files', 'prescriptions', 'dental_record', 'scribing_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Handle encrypted fields
        notes = validated_data.pop('notes', '')
        diagnosis = validated_data.pop('diagnosis', '')
        treatment_plan = validated_data.pop('treatment_plan', '')
        
        record = MedicalRecord(**validated_data)
        record.notes = notes
        record.diagnosis = diagnosis
        record.treatment_plan = treatment_plan
        record.save()
        
        return record
    
    def update(self, instance, validated_data):
        # Handle encrypted fields
        if 'notes' in validated_data:
            instance.notes = validated_data.pop('notes')
        if 'diagnosis' in validated_data:
            instance.diagnosis = validated_data.pop('diagnosis')
        if 'treatment_plan' in validated_data:
            instance.treatment_plan = validated_data.pop('treatment_plan')
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class MedicalRecordListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for medical record lists."""
    
    doctor_name = serializers.CharField(source='doctor.user.full_name', read_only=True)
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'record_type', 'record_date', 'doctor_name',
            'clinic_name', 'chief_complaint', 'created_at'
        ]


class FileUploadSerializer(serializers.Serializer):
    """Serializer for file upload requests."""
    
    file_type = serializers.ChoiceField(choices=MedicalFile.FILE_TYPES)
    file_name = serializers.CharField(max_length=255)
    mime_type = serializers.CharField(max_length=100)
    description = serializers.CharField(required=False, allow_blank=True)


class ImageAnnotationSerializer(serializers.Serializer):
    """Serializer for image annotation updates."""
    
    annotations = serializers.JSONField()
