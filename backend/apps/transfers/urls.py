"""
URL patterns for transfers.
"""
from django.urls import path
from .views import (
    PatientAccessRequestView, PatientAccessListView,
    PendingAccessRequestsView, PatientAccessRespondView,
    PatientAccessRevokeView, ValidateTokenView,
    TransferRequestCreateView, TransferRequestListView,
    TransferRequestDetailView, TransferRequestRespondView
)

app_name = 'transfers'

urlpatterns = [
    # Patient Access
    path('access/request/', PatientAccessRequestView.as_view(), name='access_request'),
    path('access/', PatientAccessListView.as_view(), name='access_list'),
    path('access/pending/', PendingAccessRequestsView.as_view(), name='access_pending'),
    path('access/<uuid:pk>/respond/', PatientAccessRespondView.as_view(), name='access_respond'),
    path('access/<uuid:pk>/revoke/', PatientAccessRevokeView.as_view(), name='access_revoke'),
    path('token/validate/', ValidateTokenView.as_view(), name='token_validate'),
    
    # Transfer Requests
    path('', TransferRequestListView.as_view(), name='transfer_list'),
    path('create/', TransferRequestCreateView.as_view(), name='transfer_create'),
    path('<uuid:pk>/', TransferRequestDetailView.as_view(), name='transfer_detail'),
    path('<uuid:pk>/respond/', TransferRequestRespondView.as_view(), name='transfer_respond'),
]
