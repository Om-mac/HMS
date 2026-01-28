"""
Views for patient management.
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from .models import Patient, PatientAllergy, PatientMedication, PatientChronicCondition, Waitlist
from .serializers import (
    PatientSerializer, PatientCreateSerializer, PatientListSerializer,
    PatientAllergySerializer, PatientMedicationSerializer,
    PatientChronicConditionSerializer, WaitlistSerializer
)
from apps.core.permissions import IsDoctor, IsPatient, HasPatientAccess
from apps.core.qr_utils import generate_patient_qr


class PatientProfileView(generics.RetrieveUpdateAPIView):
    """Get or update the current patient's profile."""
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        patient, created = Patient.objects.get_or_create(user=self.request.user)
        return patient
    
    def update(self, request, *args, **kwargs):
        serializer = PatientCreateSerializer(
            self.get_object(),
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(PatientSerializer(self.get_object()).data)


class PatientDetailView(generics.RetrieveAPIView):
    """Get patient details by ID (for doctors with access)."""
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, HasPatientAccess]
    queryset = Patient.objects.all()
    lookup_field = 'patient_id'


class PatientListView(generics.ListAPIView):
    """List all patients (for doctors)."""
    serializer_class = PatientListSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    queryset = Patient.objects.filter(is_active=True)
    filterset_fields = ['blood_type', 'gender']
    search_fields = ['user__first_name', 'user__last_name', 'patient_id']


class PatientSearchView(APIView):
    """Search for a patient by patient_id or QR code."""
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    
    def get(self, request):
        patient_id = request.query_params.get('patient_id')
        
        if not patient_id:
            return Response(
                {'error': 'patient_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            patient = Patient.objects.get(patient_id=patient_id)
            return Response(PatientListSerializer(patient).data)
        except Patient.DoesNotExist:
            return Response(
                {'error': 'Patient not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class PatientQRCodeView(APIView):
    """Generate QR code for a patient."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        try:
            patient = Patient.objects.get(user=request.user)
            qr_base64 = patient.get_qr_code()
            return Response({
                'patient_id': patient.patient_id,
                'qr_code': f'data:image/png;base64,{qr_base64}'
            })
        except Patient.DoesNotExist:
            return Response(
                {'error': 'Patient profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )


# Allergy views
class PatientAllergyListCreateView(generics.ListCreateAPIView):
    """List and create allergies for a patient."""
    serializer_class = PatientAllergySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        patient = get_object_or_404(Patient, user=self.request.user)
        return PatientAllergy.objects.filter(patient=patient)
    
    def perform_create(self, serializer):
        patient = get_object_or_404(Patient, user=self.request.user)
        serializer.save(patient=patient)


class PatientAllergyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a patient allergy."""
    serializer_class = PatientAllergySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        patient = get_object_or_404(Patient, user=self.request.user)
        return PatientAllergy.objects.filter(patient=patient)


# Medication views
class PatientMedicationListCreateView(generics.ListCreateAPIView):
    """List and create medications for a patient."""
    serializer_class = PatientMedicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        patient = get_object_or_404(Patient, user=self.request.user)
        return PatientMedication.objects.filter(patient=patient)
    
    def perform_create(self, serializer):
        patient = get_object_or_404(Patient, user=self.request.user)
        serializer.save(patient=patient)


class PatientMedicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a patient medication."""
    serializer_class = PatientMedicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        patient = get_object_or_404(Patient, user=self.request.user)
        return PatientMedication.objects.filter(patient=patient)


# Chronic condition views
class PatientConditionListCreateView(generics.ListCreateAPIView):
    """List and create chronic conditions for a patient."""
    serializer_class = PatientChronicConditionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        patient = get_object_or_404(Patient, user=self.request.user)
        return PatientChronicCondition.objects.filter(patient=patient)
    
    def perform_create(self, serializer):
        patient = get_object_or_404(Patient, user=self.request.user)
        serializer.save(patient=patient)


class PatientConditionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a patient chronic condition."""
    serializer_class = PatientChronicConditionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        patient = get_object_or_404(Patient, user=self.request.user)
        return PatientChronicCondition.objects.filter(patient=patient)


# Waitlist views
class WaitlistListCreateView(generics.ListCreateAPIView):
    """List and create waitlist entries."""
    serializer_class = WaitlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'patient':
            patient = get_object_or_404(Patient, user=user)
            return Waitlist.objects.filter(patient=patient)
        elif user.user_type == 'doctor':
            return Waitlist.objects.filter(doctor__user=user)
        return Waitlist.objects.none()
    
    def perform_create(self, serializer):
        patient = get_object_or_404(Patient, user=self.request.user)
        serializer.save(patient=patient)


class WaitlistDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a waitlist entry."""
    serializer_class = WaitlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Waitlist.objects.all()
