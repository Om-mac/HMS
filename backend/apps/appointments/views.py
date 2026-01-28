"""
Views for appointment management.
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import date, datetime, timedelta

from .models import Appointment, AppointmentHistory, LiveQueue
from .serializers import (
    AppointmentSerializer, AppointmentCreateSerializer, AppointmentListSerializer,
    AppointmentRescheduleSerializer, AppointmentStatusSerializer,
    LiveQueueSerializer, DoctorDashboardStatsSerializer
)
from apps.core.permissions import IsDoctor, IsPatient
from apps.patients.models import Patient
from apps.doctors.models import Doctor


class AppointmentListCreateView(generics.ListCreateAPIView):
    """List and create appointments."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AppointmentCreateSerializer
        return AppointmentListSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.filter(is_active=True)
        
        if user.user_type == 'patient':
            patient = get_object_or_404(Patient, user=user)
            queryset = queryset.filter(patient=patient)
        elif user.user_type == 'doctor':
            doctor = get_object_or_404(Doctor, user=user)
            queryset = queryset.filter(doctor=doctor)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(appointment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(appointment_date__lte=end_date)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('appointment_date', 'start_time')
    
    def perform_create(self, serializer):
        user = self.request.user
        if user.user_type == 'patient':
            patient = get_object_or_404(Patient, user=user)
            serializer.save(patient=patient)
        else:
            serializer.save()


class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an appointment."""
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.filter(is_active=True)
        
        if user.user_type == 'patient':
            patient = get_object_or_404(Patient, user=user)
            queryset = queryset.filter(patient=patient)
        elif user.user_type == 'doctor':
            doctor = get_object_or_404(Doctor, user=user)
            queryset = queryset.filter(doctor=doctor)
        
        return queryset


class AppointmentRescheduleView(APIView):
    """Reschedule an appointment."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        serializer = AppointmentRescheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Store original values
        if not appointment.original_date:
            appointment.original_date = appointment.appointment_date
            appointment.original_time = appointment.start_time
        
        # Update appointment
        appointment.appointment_date = serializer.validated_data['new_date']
        appointment.start_time = serializer.validated_data['new_start_time']
        appointment.end_time = serializer.validated_data['new_end_time']
        appointment.reschedule_reason = serializer.validated_data.get('reason', '')
        appointment.rescheduled_by = request.user
        appointment.status = 'rescheduled'
        appointment._changed_by = request.user
        appointment.save()
        
        return Response(AppointmentSerializer(appointment).data)


class AppointmentStatusUpdateView(APIView):
    """Update appointment status."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        serializer = AppointmentStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        appointment._changed_by = request.user
        appointment.status = serializer.validated_data['status']
        
        if serializer.validated_data.get('notes'):
            appointment.doctor_notes = serializer.validated_data['notes']
        
        appointment.save()
        
        return Response(AppointmentSerializer(appointment).data)


class AppointmentCheckInView(APIView):
    """Check-in for an appointment."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        
        if appointment.status not in ['scheduled', 'confirmed']:
            return Response(
                {'error': 'Cannot check in for this appointment'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = 'checked_in'
        appointment.checked_in_at = timezone.now()
        appointment._changed_by = request.user
        appointment.save()
        
        # Add to live queue
        queue_position = LiveQueue.objects.filter(
            clinic=appointment.clinic,
            doctor=appointment.doctor,
            status__in=['waiting', 'called']
        ).count() + 1
        
        LiveQueue.objects.create(
            appointment=appointment,
            clinic=appointment.clinic,
            doctor=appointment.doctor,
            queue_position=queue_position,
            status='waiting'
        )
        
        return Response({
            'success': True,
            'message': 'Check-in successful',
            'queue_position': queue_position,
            'token_number': appointment.token_number
        })


class TodayAppointmentsView(generics.ListAPIView):
    """Get today's appointments for a doctor."""
    serializer_class = AppointmentListSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    
    def get_queryset(self):
        doctor = get_object_or_404(Doctor, user=self.request.user)
        return Appointment.objects.filter(
            doctor=doctor,
            appointment_date=date.today(),
            is_active=True
        ).order_by('start_time')


class UpcomingAppointmentsView(generics.ListAPIView):
    """Get upcoming appointments."""
    serializer_class = AppointmentListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Appointment.objects.filter(
            appointment_date__gte=date.today(),
            status__in=['scheduled', 'confirmed', 'rescheduled'],
            is_active=True
        )
        
        if user.user_type == 'patient':
            patient = get_object_or_404(Patient, user=user)
            queryset = queryset.filter(patient=patient)
        elif user.user_type == 'doctor':
            doctor = get_object_or_404(Doctor, user=user)
            queryset = queryset.filter(doctor=doctor)
        
        return queryset.order_by('appointment_date', 'start_time')[:10]


class LiveQueueView(generics.ListAPIView):
    """Get live queue for a doctor/clinic."""
    serializer_class = LiveQueueSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        today = date.today()
        
        queryset = LiveQueue.objects.filter(
            appointment__appointment_date=today,
            status__in=['waiting', 'called', 'with_doctor']
        )
        
        if user.user_type == 'doctor':
            doctor = get_object_or_404(Doctor, user=user)
            queryset = queryset.filter(doctor=doctor)
        
        clinic_id = self.request.query_params.get('clinic')
        if clinic_id:
            queryset = queryset.filter(clinic_id=clinic_id)
        
        return queryset.order_by('queue_position')


class CallNextPatientView(APIView):
    """Call the next patient from the queue."""
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    
    def post(self, request):
        doctor = get_object_or_404(Doctor, user=request.user)
        today = date.today()
        
        # Get next waiting patient
        next_patient = LiveQueue.objects.filter(
            doctor=doctor,
            appointment__appointment_date=today,
            status='waiting'
        ).order_by('queue_position').first()
        
        if not next_patient:
            return Response(
                {'message': 'No patients in queue'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update queue status
        next_patient.status = 'called'
        next_patient.called_at = timezone.now()
        next_patient.save()
        
        # Update appointment status
        next_patient.appointment.status = 'in_progress'
        next_patient.appointment._changed_by = request.user
        next_patient.appointment.save()
        
        return Response(LiveQueueSerializer(next_patient).data)


class DoctorDashboardStatsView(APIView):
    """Get dashboard statistics for a doctor."""
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    
    def get(self, request):
        doctor = get_object_or_404(Doctor, user=request.user)
        today = date.today()
        
        today_appointments = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=today,
            is_active=True
        )
        
        stats = {
            'total_today': today_appointments.count(),
            'checked_in': today_appointments.filter(status='checked_in').count(),
            'in_progress': today_appointments.filter(status='in_progress').count(),
            'completed': today_appointments.filter(status='completed').count(),
            'pending': today_appointments.filter(status__in=['scheduled', 'confirmed']).count(),
            'cancelled': today_appointments.filter(status='cancelled').count(),
            'no_show': today_appointments.filter(status='no_show').count(),
            'average_consultation_time': 0
        }
        
        # Calculate average consultation time
        completed = today_appointments.filter(status='completed')
        if completed.exists():
            # This would need actual start/end tracking
            stats['average_consultation_time'] = 15.0  # Placeholder
        
        return Response(DoctorDashboardStatsSerializer(stats).data)
