"""
URL patterns for appointment management.
"""
from django.urls import path
from .views import (
    AppointmentListCreateView, AppointmentDetailView,
    AppointmentRescheduleView, AppointmentStatusUpdateView,
    AppointmentCheckInView, TodayAppointmentsView,
    UpcomingAppointmentsView, LiveQueueView, CallNextPatientView,
    DoctorDashboardStatsView
)

app_name = 'appointments'

urlpatterns = [
    path('', AppointmentListCreateView.as_view(), name='list_create'),
    path('today/', TodayAppointmentsView.as_view(), name='today'),
    path('upcoming/', UpcomingAppointmentsView.as_view(), name='upcoming'),
    path('queue/', LiveQueueView.as_view(), name='queue'),
    path('queue/call-next/', CallNextPatientView.as_view(), name='call_next'),
    path('dashboard/stats/', DoctorDashboardStatsView.as_view(), name='dashboard_stats'),
    path('<uuid:pk>/', AppointmentDetailView.as_view(), name='detail'),
    path('<uuid:pk>/reschedule/', AppointmentRescheduleView.as_view(), name='reschedule'),
    path('<uuid:pk>/status/', AppointmentStatusUpdateView.as_view(), name='status_update'),
    path('<uuid:pk>/check-in/', AppointmentCheckInView.as_view(), name='check_in'),
]
