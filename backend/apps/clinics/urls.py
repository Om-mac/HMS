"""
URL patterns for clinic management.
"""
from django.urls import path
from .views import (
    ClinicListView, ClinicDetailView, ClinicCreateView, ClinicUpdateView,
    ClinicFacilityListCreateView, ClinicHolidayListCreateView
)

app_name = 'clinics'

urlpatterns = [
    path('', ClinicListView.as_view(), name='list'),
    path('create/', ClinicCreateView.as_view(), name='create'),
    path('<uuid:pk>/', ClinicDetailView.as_view(), name='detail'),
    path('<uuid:pk>/update/', ClinicUpdateView.as_view(), name='update'),
    path('<uuid:clinic_id>/facilities/', ClinicFacilityListCreateView.as_view(), name='facilities'),
    path('<uuid:clinic_id>/holidays/', ClinicHolidayListCreateView.as_view(), name='holidays'),
]
