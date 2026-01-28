"""
Audit middleware for automatic logging.
"""
import logging
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

logger = logging.getLogger('apps.audit')


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log certain actions.
    """
    
    # Paths to audit for read operations
    AUDIT_READ_PATHS = [
        '/api/patients/',
        '/api/emr/',
        '/api/appointments/',
    ]
    
    def process_response(self, request, response):
        """Log successful API requests to sensitive resources."""
        if not settings.AUDIT_LOG_ENABLED:
            return response
        
        # Only log successful requests
        if response.status_code not in [200, 201]:
            return response
        
        # Only log authenticated requests
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return response
        
        # Check if path should be audited
        path = request.path
        should_audit = any(path.startswith(p) for p in self.AUDIT_READ_PATHS)
        
        if should_audit and request.method == 'GET':
            self._log_read_access(request, response)
        
        return response
    
    def _log_read_access(self, request, response):
        """Log read access to sensitive data."""
        from apps.audit.models import AuditLog
        
        try:
            # Determine resource type from path
            path = request.path
            resource_type = 'unknown'
            
            if '/patients/' in path:
                resource_type = 'patient'
            elif '/emr/' in path or '/medical' in path:
                resource_type = 'medical_record'
            elif '/appointments/' in path:
                resource_type = 'appointment'
            
            # Extract resource ID if present
            resource_id = ''
            parts = path.strip('/').split('/')
            for part in parts:
                if self._is_uuid(part):
                    resource_id = part
                    break
            
            AuditLog.log(
                user=request.user,
                action='read',
                resource_type=resource_type,
                resource_id=resource_id,
                description=f"Accessed {resource_type} data via {path}",
                request=request
            )
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
    
    @staticmethod
    def _is_uuid(value):
        """Check if a string is a valid UUID."""
        import uuid
        try:
            uuid.UUID(str(value))
            return True
        except ValueError:
            return False
