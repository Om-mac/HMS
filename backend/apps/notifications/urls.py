"""
URL patterns for notifications.
"""
from django.urls import path
from .views import (
    NotificationListView, NotificationDetailView,
    NotificationTemplateListView, NotificationTemplateCreateView
)

app_name = 'notifications'

urlpatterns = [
    path('', NotificationListView.as_view(), name='list'),
    path('<uuid:pk>/', NotificationDetailView.as_view(), name='detail'),
    path('templates/', NotificationTemplateListView.as_view(), name='template_list'),
    path('templates/create/', NotificationTemplateCreateView.as_view(), name='template_create'),
]
