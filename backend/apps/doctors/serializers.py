"""
Serializers for doctor management.
"""
from rest_framework import serializers
from .models import Doctor, Specialization, DoctorClinic, DoctorSchedule, DoctorLeave
from apps.users.serializers import UserSerializer


class SpecializationSerializer(serializers.ModelSerializer):
    """Serializer for medical specializations."""
    
    class Meta:
        model = Specialization
        fields = ['id', 'name', 'description', 'icon']


class DoctorScheduleSerializer(serializers.ModelSerializer):
    """Serializer for doctor schedules."""
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = DoctorSchedule
        fields = [
            'id', 'day_of_week', 'day_name', 'start_time', 'end_time',
            'break_start', 'break_end', 'slot_duration', 'max_patients'
        ]


class DoctorClinicSerializer(serializers.ModelSerializer):
    """Serializer for doctor-clinic associations."""
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    clinic_address = serializers.CharField(source='clinic.address', read_only=True)
    schedules = DoctorScheduleSerializer(many=True, read_only=True)
    
    class Meta:
        model = DoctorClinic
        fields = [
            'id', 'clinic', 'clinic_name', 'clinic_address',
            'consultation_fee', 'is_primary', 'is_active', 'schedules'
        ]


class DoctorSerializer(serializers.ModelSerializer):
    """Serializer for doctor profile."""
    
    user = UserSerializer(read_only=True)
    specializations = SpecializationSerializer(many=True, read_only=True)
    doctor_clinics = DoctorClinicSerializer(many=True, read_only=True)
    specialization_list = serializers.ReadOnlyField()
    
    class Meta:
        model = Doctor
        fields = [
            'id', 'user', 'registration_number', 'specializations',
            'specialization_list', 'qualification', 'experience_years',
            'bio', 'consultation_fee', 'consultation_duration',
            'doctor_clinics', 'average_rating', 'total_reviews',
            'is_accepting_patients', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'average_rating', 'total_reviews', 'created_at', 'updated_at']


class DoctorCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating doctor profile."""
    
    specialization_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Doctor
        fields = [
            'registration_number', 'qualification', 'experience_years',
            'bio', 'consultation_fee', 'consultation_duration',
            'is_accepting_patients', 'specialization_ids'
        ]
    
    def create(self, validated_data):
        specialization_ids = validated_data.pop('specialization_ids', [])
        doctor = Doctor.objects.create(**validated_data)
        if specialization_ids:
            doctor.specializations.set(Specialization.objects.filter(id__in=specialization_ids))
        return doctor
    
    def update(self, instance, validated_data):
        specialization_ids = validated_data.pop('specialization_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if specialization_ids is not None:
            instance.specializations.set(Specialization.objects.filter(id__in=specialization_ids))
        return instance


class DoctorListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for doctor lists."""
    
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    specialization_list = serializers.ReadOnlyField()
    profile_picture = serializers.ImageField(source='user.profile_picture', read_only=True)
    
    class Meta:
        model = Doctor
        fields = [
            'id', 'full_name', 'email', 'specialization_list',
            'qualification', 'experience_years', 'consultation_fee',
            'average_rating', 'total_reviews', 'is_accepting_patients',
            'profile_picture'
        ]


class DoctorLeaveSerializer(serializers.ModelSerializer):
    """Serializer for doctor leaves."""
    
    class Meta:
        model = DoctorLeave
        fields = [
            'id', 'clinic', 'leave_type', 'start_date', 'end_date',
            'start_time', 'end_time', 'reason', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
