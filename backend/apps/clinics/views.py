"""
Views for clinic management.
"""
from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404

from .models import Clinic, ClinicFacility, ClinicHoliday
from .serializers import (
    ClinicSerializer, ClinicListSerializer, ClinicCreateSerializer,
    ClinicFacilitySerializer, ClinicHolidaySerializer
)
from apps.core.permissions import IsClinicAdmin


class ClinicListView(generics.ListAPIView):
    """List all clinics."""
    serializer_class = ClinicListSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Clinic.objects.filter(is_active=True)
    filterset_fields = ['clinic_type', 'city', 'has_emergency', 'has_pharmacy', 'has_lab']
    search_fields = ['name', 'city', 'address']


class ClinicDetailView(generics.RetrieveAPIView):
    """Get clinic details."""
    serializer_class = ClinicSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Clinic.objects.filter(is_active=True)


class ClinicCreateView(generics.CreateAPIView):
    """Create a new clinic (admin only)."""
    serializer_class = ClinicCreateSerializer
    permission_classes = [permissions.IsAdminUser]


class ClinicUpdateView(generics.UpdateAPIView):
    """Update clinic details."""
    serializer_class = ClinicCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsClinicAdmin]
    queryset = Clinic.objects.all()
    
    def get_queryset(self):
        return Clinic.objects.filter(admin_user=self.request.user)


class ClinicDoctorsView(generics.ListAPIView):
    """List doctors at a specific clinic."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, pk):
        from apps.doctors.serializers import DoctorListSerializer
        clinic = get_object_or_404(Clinic, pk=pk)
        doctors = clinic.doctors.filter(is_active=True)
        serializer = DoctorListSerializer(doctors, many=True)
        return Response(serializer.data)


class ClinicFacilityListCreateView(generics.ListCreateAPIView):
    """List and create clinic facilities."""
    serializer_class = ClinicFacilitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        clinic_id = self.kwargs.get('clinic_id')
        return ClinicFacility.objects.filter(clinic_id=clinic_id)
    
    def perform_create(self, serializer):
        clinic_id = self.kwargs.get('clinic_id')
        clinic = get_object_or_404(Clinic, id=clinic_id)
        serializer.save(clinic=clinic)


class ClinicHolidayListCreateView(generics.ListCreateAPIView):
    """List and create clinic holidays."""
    serializer_class = ClinicHolidaySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        clinic_id = self.kwargs.get('clinic_id')
        return ClinicHoliday.objects.filter(clinic_id=clinic_id)
    
    def perform_create(self, serializer):
        clinic_id = self.kwargs.get('clinic_id')
        clinic = get_object_or_404(Clinic, id=clinic_id)
        serializer.save(clinic=clinic)
