"""
URL patterns for doctor management.
"""
from django.urls import path
from .views import (
    DoctorProfileView, DoctorDetailView, DoctorListView,
    SpecializationListView, DoctorAvailabilityView,
    DoctorScheduleListCreateView, DoctorScheduleDetailView,
    DoctorLeaveListCreateView, DoctorLeaveDetailView
)

app_name = 'doctors'

urlpatterns = [
    # Doctor profile
    path('profile/', DoctorProfileView.as_view(), name='profile'),
    path('list/', DoctorListView.as_view(), name='list'),
    path('<uuid:pk>/', DoctorDetailView.as_view(), name='detail'),
    path('<uuid:doctor_id>/availability/', DoctorAvailabilityView.as_view(), name='availability'),
    
    # Specializations
    path('specializations/', SpecializationListView.as_view(), name='specialization_list'),
    
    # Schedules
    path('schedules/', DoctorScheduleListCreateView.as_view(), name='schedule_list'),
    path('schedules/<uuid:pk>/', DoctorScheduleDetailView.as_view(), name='schedule_detail'),
    
    # Leaves
    path('leaves/', DoctorLeaveListCreateView.as_view(), name='leave_list'),
    path('leaves/<uuid:pk>/', DoctorLeaveDetailView.as_view(), name='leave_detail'),
]
