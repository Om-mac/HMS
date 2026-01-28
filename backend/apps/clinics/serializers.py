"""
Serializers for clinic management.
"""
from rest_framework import serializers
from .models import Clinic, ClinicFacility, ClinicHoliday


class ClinicFacilitySerializer(serializers.ModelSerializer):
    """Serializer for clinic facilities."""
    
    class Meta:
        model = ClinicFacility
        fields = ['id', 'name', 'description', 'is_available']


class ClinicHolidaySerializer(serializers.ModelSerializer):
    """Serializer for clinic holidays."""
    
    class Meta:
        model = ClinicHoliday
        fields = ['id', 'date', 'reason']


class ClinicSerializer(serializers.ModelSerializer):
    """Serializer for clinic details."""
    
    facilities = ClinicFacilitySerializer(many=True, read_only=True)
    
    class Meta:
        model = Clinic
        fields = [
            'id', 'name', 'clinic_type', 'registration_number',
            'phone', 'email', 'website', 'address', 'city', 'state',
            'country', 'postal_code', 'latitude', 'longitude',
            'opening_time', 'closing_time', 'has_pharmacy', 'has_lab',
            'has_emergency', 'has_ambulance', 'logo', 'average_rating',
            'total_reviews', 'facilities', 'created_at'
        ]
        read_only_fields = ['id', 'average_rating', 'total_reviews', 'created_at']


class ClinicListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for clinic lists."""
    
    doctor_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Clinic
        fields = [
            'id', 'name', 'clinic_type', 'phone', 'address', 'city',
            'state', 'logo', 'average_rating', 'has_emergency', 'doctor_count'
        ]
    
    def get_doctor_count(self, obj):
        return obj.doctors.count()


class ClinicCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating clinics."""
    
    class Meta:
        model = Clinic
        fields = [
            'name', 'clinic_type', 'registration_number', 'phone', 'email',
            'website', 'address', 'city', 'state', 'country', 'postal_code',
            'latitude', 'longitude', 'opening_time', 'closing_time',
            'has_pharmacy', 'has_lab', 'has_emergency', 'has_ambulance', 'logo'
        ]
