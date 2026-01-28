"""
URL patterns for patient management.
"""
from django.urls import path
from .views import (
    PatientProfileView, PatientDetailView, PatientListView,
    PatientSearchView, PatientQRCodeView,
    PatientAllergyListCreateView, PatientAllergyDetailView,
    PatientMedicationListCreateView, PatientMedicationDetailView,
    PatientConditionListCreateView, PatientConditionDetailView,
    WaitlistListCreateView, WaitlistDetailView
)

app_name = 'patients'

urlpatterns = [
    # Patient profile
    path('profile/', PatientProfileView.as_view(), name='profile'),
    path('search/', PatientSearchView.as_view(), name='search'),
    path('qr-code/', PatientQRCodeView.as_view(), name='qr_code'),
    path('list/', PatientListView.as_view(), name='list'),
    path('<str:patient_id>/', PatientDetailView.as_view(), name='detail'),
    
    # Allergies
    path('allergies/', PatientAllergyListCreateView.as_view(), name='allergy_list'),
    path('allergies/<uuid:pk>/', PatientAllergyDetailView.as_view(), name='allergy_detail'),
    
    # Medications
    path('medications/', PatientMedicationListCreateView.as_view(), name='medication_list'),
    path('medications/<uuid:pk>/', PatientMedicationDetailView.as_view(), name='medication_detail'),
    
    # Chronic conditions
    path('conditions/', PatientConditionListCreateView.as_view(), name='condition_list'),
    path('conditions/<uuid:pk>/', PatientConditionDetailView.as_view(), name='condition_detail'),
    
    # Waitlist
    path('waitlist/', WaitlistListCreateView.as_view(), name='waitlist_list'),
    path('waitlist/<uuid:pk>/', WaitlistDetailView.as_view(), name='waitlist_detail'),
]
