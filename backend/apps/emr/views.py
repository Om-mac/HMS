"""
Views for EMR management.
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
import uuid

from .models import (
    MedicalRecord, MedicalFile, Prescription, PrescriptionItem,
    DentalRecord, ToothHistory, AmbientScribingNote
)
from .serializers import (
    MedicalRecordSerializer, MedicalRecordListSerializer,
    MedicalFileSerializer, PrescriptionSerializer, PrescriptionItemSerializer,
    DentalRecordSerializer, ToothHistorySerializer, AmbientScribingNoteSerializer,
    FileUploadSerializer, ImageAnnotationSerializer
)
from apps.core.permissions import IsDoctor, HasPatientAccess
from apps.core.s3_utils import generate_upload_presigned_url, generate_presigned_url
from apps.patients.models import Patient
from apps.doctors.models import Doctor


class MedicalRecordListCreateView(generics.ListCreateAPIView):
    """List and create medical records."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MedicalRecordSerializer
        return MedicalRecordListSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = MedicalRecord.objects.filter(is_active=True)
        
        if user.user_type == 'patient':
            patient = get_object_or_404(Patient, user=user)
            queryset = queryset.filter(patient=patient)
        elif user.user_type == 'doctor':
            doctor = get_object_or_404(Doctor, user=user)
            queryset = queryset.filter(doctor=doctor)
        
        # Filter by patient
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        # Filter by record type
        record_type = self.request.query_params.get('type')
        if record_type:
            queryset = queryset.filter(record_type=record_type)
        
        return queryset.order_by('-record_date', '-created_at')
    
    def perform_create(self, serializer):
        doctor = get_object_or_404(Doctor, user=self.request.user)
        serializer.save(doctor=doctor)


class MedicalRecordDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update a medical record."""
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated, HasPatientAccess]
    queryset = MedicalRecord.objects.filter(is_active=True)


class PatientMedicalHistoryView(generics.ListAPIView):
    """Get complete medical history for a patient."""
    serializer_class = MedicalRecordListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        patient_id = self.kwargs.get('patient_id')
        return MedicalRecord.objects.filter(
            patient_id=patient_id,
            is_active=True
        ).order_by('-record_date')


class FileUploadURLView(APIView):
    """Generate presigned URL for file upload."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, record_id):
        serializer = FileUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Generate unique S3 key
        file_ext = serializer.validated_data['file_name'].split('.')[-1]
        s3_key = f"medical_files/{record_id}/{uuid.uuid4()}.{file_ext}"
        
        # Generate upload URL
        upload_data = generate_upload_presigned_url(
            s3_key,
            serializer.validated_data['mime_type']
        )
        
        return Response({
            's3_key': s3_key,
            'upload_url': upload_data['url'],
            'fields': upload_data['fields']
        })


class FileUploadCompleteView(APIView):
    """Complete file upload and create MedicalFile record."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, record_id):
        record = get_object_or_404(MedicalRecord, id=record_id)
        
        file_data = MedicalFile.objects.create(
            medical_record=record,
            patient=record.patient,
            uploaded_by=request.user,
            file_type=request.data.get('file_type', 'document'),
            file_name=request.data.get('file_name'),
            file_path=request.data.get('s3_key'),
            file_size=request.data.get('file_size', 0),
            mime_type=request.data.get('mime_type'),
            description=request.data.get('description', '')
        )
        
        return Response(MedicalFileSerializer(file_data).data, status=status.HTTP_201_CREATED)


class MedicalFileDetailView(generics.RetrieveDestroyAPIView):
    """Retrieve or delete a medical file."""
    serializer_class = MedicalFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = MedicalFile.objects.all()


class ImageAnnotationView(APIView):
    """Update image annotations."""
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    
    def put(self, request, file_id):
        file = get_object_or_404(MedicalFile, id=file_id)
        serializer = ImageAnnotationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        file.annotations = serializer.validated_data['annotations']
        file.save()
        
        return Response(MedicalFileSerializer(file).data)


class PrescriptionCreateView(generics.CreateAPIView):
    """Create a prescription."""
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    
    def perform_create(self, serializer):
        doctor = get_object_or_404(Doctor, user=self.request.user)
        serializer.save(doctor=doctor)


class PrescriptionDetailView(generics.RetrieveAPIView):
    """Get prescription details."""
    serializer_class = PrescriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Prescription.objects.all()


class PrescriptionAddItemView(APIView):
    """Add item to prescription."""
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    
    def post(self, request, prescription_id):
        prescription = get_object_or_404(Prescription, id=prescription_id)
        serializer = PrescriptionItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        item = PrescriptionItem.objects.create(
            prescription=prescription,
            **serializer.validated_data
        )
        
        return Response(PrescriptionItemSerializer(item).data, status=status.HTTP_201_CREATED)


class PrescriptionSignView(APIView):
    """Sign a prescription digitally."""
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    
    def post(self, request, prescription_id):
        prescription = get_object_or_404(Prescription, id=prescription_id)
        
        if prescription.is_signed:
            return Response(
                {'error': 'Prescription already signed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        prescription.is_signed = True
        prescription.signed_at = timezone.now()
        prescription.save()
        
        return Response(PrescriptionSerializer(prescription).data)


# Dental-specific views
class ToothHistoryListView(generics.ListAPIView):
    """Get history for a specific tooth."""
    serializer_class = ToothHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        patient_id = self.kwargs.get('patient_id')
        tooth_number = self.kwargs.get('tooth_number')
        
        return ToothHistory.objects.filter(
            patient_id=patient_id,
            tooth_number=tooth_number
        ).order_by('-procedure_date')


class ToothHistoryCreateView(generics.CreateAPIView):
    """Add tooth history entry."""
    serializer_class = ToothHistorySerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    
    def perform_create(self, serializer):
        patient_id = self.kwargs.get('patient_id')
        patient = get_object_or_404(Patient, id=patient_id)
        serializer.save(patient=patient)


class DentalOdontogramView(APIView):
    """Get/update dental odontogram for a patient."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, patient_id):
        patient = get_object_or_404(Patient, id=patient_id)
        
        # Get all tooth history grouped by tooth
        tooth_history = ToothHistory.objects.filter(
            patient=patient
        ).order_by('tooth_number', '-procedure_date')
        
        # Build odontogram data
        odontogram = {}
        for i in range(1, 33):
            history = tooth_history.filter(tooth_number=i)
            odontogram[str(i)] = {
                'status': 'healthy',
                'procedures': ToothHistorySerializer(history, many=True).data
            }
            
            # Determine current status from most recent procedure
            if history.exists():
                latest = history.first()
                if latest.procedure == 'extraction':
                    odontogram[str(i)]['status'] = 'extracted'
                elif latest.procedure in ['cavity', 'filling']:
                    odontogram[str(i)]['status'] = 'treated'
                elif latest.procedure == 'root_canal':
                    odontogram[str(i)]['status'] = 'root_canal'
        
        return Response(odontogram)


# Ambient Scribing views
class AmbientScribingStartView(APIView):
    """Start ambient scribing for a consultation."""
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    
    def post(self, request, record_id):
        record = get_object_or_404(MedicalRecord, id=record_id)
        
        scribing_note = AmbientScribingNote.objects.create(
            medical_record=record,
            status='transcribing'
        )
        
        return Response({
            'id': str(scribing_note.id),
            'status': 'transcribing',
            'message': 'Ambient scribing started'
        }, status=status.HTTP_201_CREATED)


class AmbientScribingUpdateView(APIView):
    """Update/approve ambient scribing note."""
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    
    def put(self, request, note_id):
        note = get_object_or_404(AmbientScribingNote, id=note_id)
        
        if 'final_note' in request.data:
            note.final_note = request.data['final_note']
        
        if request.data.get('approve'):
            note.status = 'approved'
            note.approved_at = timezone.now()
            
            # Copy to medical record
            note.medical_record.notes = note.final_note
            note.medical_record.save()
        elif request.data.get('reviewed'):
            note.status = 'reviewed'
            note.reviewed_at = timezone.now()
        
        note.save()
        
        return Response(AmbientScribingNoteSerializer(note).data)
