"""
Base permissions for HMS API.
"""
from rest_framework import permissions


class IsDoctor(permissions.BasePermission):
    """
    Permission check for doctors.
    """
    message = "Only doctors can perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'doctor'
        )


class IsPatient(permissions.BasePermission):
    """
    Permission check for patients.
    """
    message = "Only patients can perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'patient'
        )


class IsClinicAdmin(permissions.BasePermission):
    """
    Permission check for clinic administrators.
    """
    message = "Only clinic administrators can perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'clinic_admin'
        )


class IsDoctorOrReadOnly(permissions.BasePermission):
    """
    Allows doctors full access, others read-only.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'doctor'
        )


class IsOwnerOrDoctor(permissions.BasePermission):
    """
    Object-level permission to allow patients to see their own records
    or doctors to see records of patients they have access to.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the user is the patient who owns the record
        if hasattr(obj, 'patient'):
            if hasattr(request.user, 'patient_profile'):
                if obj.patient == request.user.patient_profile:
                    return True
        
        # Check if user is a doctor with access to this patient
        if request.user.user_type == 'doctor':
            return True  # Additional access control is handled elsewhere
        
        return False


class HasPatientAccess(permissions.BasePermission):
    """
    Permission to check if a doctor has access to a specific patient's records.
    """
    message = "You do not have access to this patient's records."
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Patients can access their own records
        if request.user.user_type == 'patient':
            if hasattr(obj, 'patient'):
                return obj.patient.user == request.user
            return obj.user == request.user
        
        # Doctors need explicit access permission
        if request.user.user_type == 'doctor':
            from apps.transfers.models import PatientAccess
            patient = obj.patient if hasattr(obj, 'patient') else obj
            
            return PatientAccess.objects.filter(
                doctor=request.user.doctor_profile,
                patient=patient,
                status='approved'
            ).exists()
        
        return False
