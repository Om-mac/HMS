"""
Views for patient transfers and access management.
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import PatientAccess, PermissionToken, TransferRequest
from .serializers import (
    PatientAccessSerializer, PatientAccessRequestSerializer,
    PatientAccessResponseSerializer, PermissionTokenSerializer,
    TransferRequestSerializer, TransferRequestCreateSerializer,
    TransferResponseSerializer
)
from apps.core.permissions import IsDoctor, IsPatient
from apps.patients.models import Patient
from apps.doctors.models import Doctor


class PatientAccessRequestView(generics.CreateAPIView):
    """Request access to a patient's records."""
    serializer_class = PatientAccessRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    
    def perform_create(self, serializer):
        doctor = get_object_or_404(Doctor, user=self.request.user)
        serializer.save(doctor=doctor, status='pending')
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if request already exists
        doctor = get_object_or_404(Doctor, user=request.user)
        existing = PatientAccess.objects.filter(
            doctor=doctor,
            patient=serializer.validated_data['patient'],
            status__in=['pending', 'approved']
        ).first()
        
        if existing:
            if existing.status == 'approved':
                return Response(
                    {'message': 'You already have access to this patient'},
                    status=status.HTTP_200_OK
                )
            return Response(
                {'message': 'Access request already pending'},
                status=status.HTTP_200_OK
            )
        
        self.perform_create(serializer)
        return Response(
            {'message': 'Access request submitted successfully'},
            status=status.HTTP_201_CREATED
        )


class PatientAccessListView(generics.ListAPIView):
    """List access requests/grants."""
    serializer_class = PatientAccessSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == 'doctor':
            # Requests made by this doctor
            doctor = get_object_or_404(Doctor, user=user)
            return PatientAccess.objects.filter(doctor=doctor)
        
        elif user.user_type == 'patient':
            # Access to this patient's records
            patient = get_object_or_404(Patient, user=user)
            return PatientAccess.objects.filter(patient=patient)
        
        return PatientAccess.objects.none()


class PendingAccessRequestsView(generics.ListAPIView):
    """List pending access requests for a doctor to approve."""
    serializer_class = PatientAccessSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    
    def get_queryset(self):
        doctor = get_object_or_404(Doctor, user=self.request.user)
        
        # Get patients this doctor treats
        patient_ids = doctor.appointments.values_list('patient_id', flat=True).distinct()
        
        return PatientAccess.objects.filter(
            patient_id__in=patient_ids,
            status='pending'
        ).exclude(doctor=doctor)


class PatientAccessRespondView(APIView):
    """Respond to an access request (approve/reject)."""
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    
    def post(self, request, pk):
        access = get_object_or_404(PatientAccess, pk=pk)
        serializer = PatientAccessResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        doctor = get_object_or_404(Doctor, user=request.user)
        
        if serializer.validated_data['action'] == 'approve':
            token = access.approve(
                granted_by=doctor,
                valid_days=serializer.validated_data.get('valid_days', 30)
            )
            return Response({
                'message': 'Access approved',
                'access': PatientAccessSerializer(access).data,
                'token': token.token
            })
        else:
            access.reject(serializer.validated_data.get('reason', ''))
            return Response({
                'message': 'Access rejected',
                'access': PatientAccessSerializer(access).data
            })


class PatientAccessRevokeView(APIView):
    """Revoke a previously granted access."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        access = get_object_or_404(PatientAccess, pk=pk)
        
        # Verify user can revoke (patient or granting doctor)
        user = request.user
        can_revoke = False
        
        if user.user_type == 'patient':
            patient = get_object_or_404(Patient, user=user)
            if access.patient == patient:
                can_revoke = True
        elif user.user_type == 'doctor':
            doctor = get_object_or_404(Doctor, user=user)
            if access.granted_by == doctor:
                can_revoke = True
        
        if not can_revoke:
            return Response(
                {'error': 'You cannot revoke this access'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        access.revoke(request.data.get('reason', ''))
        return Response({
            'message': 'Access revoked',
            'access': PatientAccessSerializer(access).data
        })


class ValidateTokenView(APIView):
    """Validate a permission token."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        token_str = request.data.get('token')
        
        if not token_str:
            return Response(
                {'error': 'Token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            token = PermissionToken.objects.get(token=token_str)
            
            if token.is_valid:
                token.use()
                return Response({
                    'valid': True,
                    'access': PatientAccessSerializer(token.access).data
                })
            else:
                return Response({
                    'valid': False,
                    'reason': 'Token expired or revoked'
                })
        except PermissionToken.DoesNotExist:
            return Response({
                'valid': False,
                'reason': 'Invalid token'
            })


# Transfer Request Views
class TransferRequestCreateView(generics.CreateAPIView):
    """Create a transfer request."""
    serializer_class = TransferRequestCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    
    def perform_create(self, serializer):
        doctor = get_object_or_404(Doctor, user=self.request.user)
        # Get doctor's primary clinic
        doctor_clinic = doctor.doctor_clinics.filter(is_primary=True).first()
        clinic = doctor_clinic.clinic if doctor_clinic else doctor.clinics.first()
        
        serializer.save(
            requesting_doctor=doctor,
            requesting_clinic=clinic,
            status='pending'
        )


class TransferRequestListView(generics.ListAPIView):
    """List transfer requests."""
    serializer_class = TransferRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    
    def get_queryset(self):
        doctor = get_object_or_404(Doctor, user=self.request.user)
        
        # Get both sent and received requests
        request_type = self.request.query_params.get('type', 'all')
        
        if request_type == 'sent':
            return TransferRequest.objects.filter(requesting_doctor=doctor)
        elif request_type == 'received':
            return TransferRequest.objects.filter(receiving_doctor=doctor)
        else:
            return TransferRequest.objects.filter(
                requesting_doctor=doctor
            ) | TransferRequest.objects.filter(
                receiving_doctor=doctor
            )


class TransferRequestDetailView(generics.RetrieveAPIView):
    """Get transfer request details."""
    serializer_class = TransferRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    queryset = TransferRequest.objects.all()


class TransferRequestRespondView(APIView):
    """Respond to a transfer request."""
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    
    def post(self, request, pk):
        transfer = get_object_or_404(TransferRequest, pk=pk)
        serializer = TransferResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if serializer.validated_data['action'] == 'approve':
            transfer.approve(
                responded_by=request.user,
                notes=serializer.validated_data.get('notes', '')
            )
            return Response({
                'message': 'Transfer approved',
                'transfer': TransferRequestSerializer(transfer).data
            })
        else:
            transfer.reject(
                responded_by=request.user,
                reason=serializer.validated_data.get('notes', '')
            )
            return Response({
                'message': 'Transfer rejected',
                'transfer': TransferRequestSerializer(transfer).data
            })
