"""
URL configuration for HMS project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView


def health_check(request):
    """Health check endpoint for Render/load balancers."""
    return JsonResponse({'status': 'healthy', 'service': 'hms-backend'})


urlpatterns = [
    # Health Check
    path('api/health/', health_check, name='health_check'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Authentication
    path('api/auth/', include('apps.users.urls')),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API Endpoints
    path('api/patients/', include('apps.patients.urls')),
    path('api/doctors/', include('apps.doctors.urls')),
    path('api/clinics/', include('apps.clinics.urls')),
    path('api/appointments/', include('apps.appointments.urls')),
    path('api/emr/', include('apps.emr.urls')),
    path('api/transfers/', include('apps.transfers.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/audit/', include('apps.audit.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
