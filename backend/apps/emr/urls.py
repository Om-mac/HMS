"""
URL patterns for EMR.
"""
from django.urls import path
from .views import (
    MedicalRecordListCreateView, MedicalRecordDetailView,
    PatientMedicalHistoryView, FileUploadURLView, FileUploadCompleteView,
    MedicalFileDetailView, ImageAnnotationView, PrescriptionCreateView,
    PrescriptionDetailView, PrescriptionAddItemView, PrescriptionSignView,
    ToothHistoryListView, ToothHistoryCreateView, DentalOdontogramView,
    AmbientScribingStartView, AmbientScribingUpdateView
)

app_name = 'emr'

urlpatterns = [
    # Medical Records
    path('records/', MedicalRecordListCreateView.as_view(), name='record_list'),
    path('records/<uuid:pk>/', MedicalRecordDetailView.as_view(), name='record_detail'),
    path('records/patient/<uuid:patient_id>/', PatientMedicalHistoryView.as_view(), name='patient_history'),
    
    # File uploads
    path('records/<uuid:record_id>/upload-url/', FileUploadURLView.as_view(), name='upload_url'),
    path('records/<uuid:record_id>/upload-complete/', FileUploadCompleteView.as_view(), name='upload_complete'),
    path('files/<uuid:pk>/', MedicalFileDetailView.as_view(), name='file_detail'),
    path('files/<uuid:file_id>/annotate/', ImageAnnotationView.as_view(), name='annotate'),
    
    # Prescriptions
    path('prescriptions/create/', PrescriptionCreateView.as_view(), name='prescription_create'),
    path('prescriptions/<uuid:pk>/', PrescriptionDetailView.as_view(), name='prescription_detail'),
    path('prescriptions/<uuid:prescription_id>/items/', PrescriptionAddItemView.as_view(), name='prescription_add_item'),
    path('prescriptions/<uuid:prescription_id>/sign/', PrescriptionSignView.as_view(), name='prescription_sign'),
    
    # Dental
    path('dental/patient/<uuid:patient_id>/odontogram/', DentalOdontogramView.as_view(), name='odontogram'),
    path('dental/patient/<uuid:patient_id>/tooth/<int:tooth_number>/', ToothHistoryListView.as_view(), name='tooth_history'),
    path('dental/patient/<uuid:patient_id>/tooth/add/', ToothHistoryCreateView.as_view(), name='add_tooth_history'),
    
    # Ambient Scribing
    path('records/<uuid:record_id>/scribing/start/', AmbientScribingStartView.as_view(), name='scribing_start'),
    path('scribing/<uuid:note_id>/', AmbientScribingUpdateView.as_view(), name='scribing_update'),
]
