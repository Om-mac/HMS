"""
Views for doctor management.
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import date, datetime, timedelta

from .models import Doctor, Specialization, DoctorClinic, DoctorSchedule, DoctorLeave
from .serializers import (
    DoctorSerializer, DoctorCreateSerializer, DoctorListSerializer,
    SpecializationSerializer, DoctorClinicSerializer, DoctorScheduleSerializer,
    DoctorLeaveSerializer
)
from apps.core.permissions import IsDoctor


class DoctorProfileView(generics.RetrieveUpdateAPIView):
    """Get or update the current doctor's profile."""
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    
    def get_object(self):
        return get_object_or_404(Doctor, user=self.request.user)
    
    def update(self, request, *args, **kwargs):
        serializer = DoctorCreateSerializer(
            self.get_object(),
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(DoctorSerializer(self.get_object()).data)


class DoctorDetailView(generics.RetrieveAPIView):
    """Get doctor details by ID."""
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Doctor.objects.filter(is_active=True)


class DoctorListView(generics.ListAPIView):
    """List all doctors with filtering."""
    serializer_class = DoctorListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['is_accepting_patients']
    search_fields = ['user__first_name', 'user__last_name', 'registration_number']
    
    def get_queryset(self):
        queryset = Doctor.objects.filter(is_active=True)
        
        # Filter by specialization
        specialization = self.request.query_params.get('specialization')
        if specialization:
            queryset = queryset.filter(specializations__name__icontains=specialization)
        
        # Filter by clinic
        clinic = self.request.query_params.get('clinic')
        if clinic:
            queryset = queryset.filter(clinics__id=clinic)
        
        return queryset.distinct()


class SpecializationListView(generics.ListAPIView):
    """List all specializations."""
    serializer_class = SpecializationSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Specialization.objects.filter(is_active=True)


class DoctorAvailabilityView(APIView):
    """Get doctor's available time slots for a specific date."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, doctor_id):
        doctor = get_object_or_404(Doctor, id=doctor_id)
        date_str = request.query_params.get('date')
        clinic_id = request.query_params.get('clinic')
        
        if not date_str:
            return Response(
                {'error': 'date parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            check_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get day of week (0=Monday, 6=Sunday)
        day_of_week = check_date.weekday()
        
        # Build schedule query
        schedule_query = Q(doctor_clinic__doctor=doctor, day_of_week=day_of_week)
        if clinic_id:
            schedule_query &= Q(doctor_clinic__clinic_id=clinic_id)
        
        schedules = DoctorSchedule.objects.filter(schedule_query)
        
        # Check for leaves
        leaves = DoctorLeave.objects.filter(
            doctor=doctor,
            start_date__lte=check_date,
            end_date__gte=check_date
        )
        
        if leaves.exists():
            return Response({
                'date': date_str,
                'available': False,
                'reason': 'Doctor is on leave',
                'slots': []
            })
        
        # Generate time slots
        all_slots = []
        for schedule in schedules:
            slots = self._generate_slots(schedule, check_date)
            all_slots.extend(slots)
        
        # Get booked appointments
        from apps.appointments.models import Appointment
        booked = Appointment.objects.filter(
            doctor=doctor,
            appointment_date=check_date,
            status__in=['scheduled', 'confirmed', 'checked_in', 'in_progress']
        ).values_list('start_time', flat=True)
        
        booked_times = set(str(t)[:5] for t in booked)
        
        # Mark booked slots
        for slot in all_slots:
            slot['available'] = slot['time'] not in booked_times
        
        return Response({
            'date': date_str,
            'day': check_date.strftime('%A'),
            'doctor': DoctorListSerializer(doctor).data,
            'slots': all_slots
        })
    
    def _generate_slots(self, schedule, check_date):
        """Generate time slots from schedule."""
        slots = []
        current = datetime.combine(check_date, schedule.start_time)
        end = datetime.combine(check_date, schedule.end_time)
        duration = timedelta(minutes=schedule.slot_duration)
        
        break_start = None
        break_end = None
        if schedule.break_start and schedule.break_end:
            break_start = datetime.combine(check_date, schedule.break_start)
            break_end = datetime.combine(check_date, schedule.break_end)
        
        while current + duration <= end:
            # Skip break time
            if break_start and break_end:
                if break_start <= current < break_end:
                    current = break_end
                    continue
            
            slots.append({
                'time': current.strftime('%H:%M'),
                'clinic_id': str(schedule.doctor_clinic.clinic_id),
                'clinic_name': schedule.doctor_clinic.clinic.name,
                'duration': schedule.slot_duration,
                'available': True
            })
            current += duration
        
        return slots


# Schedule management views
class DoctorScheduleListCreateView(generics.ListCreateAPIView):
    """List and create doctor schedules."""
    serializer_class = DoctorScheduleSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    
    def get_queryset(self):
        doctor = get_object_or_404(Doctor, user=self.request.user)
        return DoctorSchedule.objects.filter(doctor_clinic__doctor=doctor)
    
    def perform_create(self, serializer):
        doctor_clinic_id = self.request.data.get('doctor_clinic')
        doctor_clinic = get_object_or_404(
            DoctorClinic,
            id=doctor_clinic_id,
            doctor__user=self.request.user
        )
        serializer.save(doctor_clinic=doctor_clinic)


class DoctorScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a doctor schedule."""
    serializer_class = DoctorScheduleSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    
    def get_queryset(self):
        doctor = get_object_or_404(Doctor, user=self.request.user)
        return DoctorSchedule.objects.filter(doctor_clinic__doctor=doctor)


# Leave management views
class DoctorLeaveListCreateView(generics.ListCreateAPIView):
    """List and create doctor leaves."""
    serializer_class = DoctorLeaveSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    
    def get_queryset(self):
        doctor = get_object_or_404(Doctor, user=self.request.user)
        return DoctorLeave.objects.filter(doctor=doctor)
    
    def perform_create(self, serializer):
        doctor = get_object_or_404(Doctor, user=self.request.user)
        serializer.save(doctor=doctor)


class DoctorLeaveDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a doctor leave."""
    serializer_class = DoctorLeaveSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    
    def get_queryset(self):
        doctor = get_object_or_404(Doctor, user=self.request.user)
        return DoctorLeave.objects.filter(doctor=doctor)
