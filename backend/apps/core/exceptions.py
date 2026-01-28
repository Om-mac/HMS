"""
Custom exception handling for HMS API.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class HMSAPIException(Exception):
    """Base exception for HMS API."""
    def __init__(self, message, code=None, status_code=status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.code = code or 'error'
        self.status_code = status_code
        super().__init__(message)


class EncryptionError(HMSAPIException):
    """Raised when encryption/decryption fails."""
    def __init__(self, message="Encryption error occurred"):
        super().__init__(message, code='encryption_error', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PermissionDeniedError(HMSAPIException):
    """Raised when access is denied."""
    def __init__(self, message="You do not have permission to perform this action"):
        super().__init__(message, code='permission_denied', status_code=status.HTTP_403_FORBIDDEN)


class TransferError(HMSAPIException):
    """Raised when patient transfer fails."""
    def __init__(self, message="Patient transfer failed"):
        super().__init__(message, code='transfer_error', status_code=status.HTTP_400_BAD_REQUEST)


class AppointmentError(HMSAPIException):
    """Raised when appointment operation fails."""
    def __init__(self, message="Appointment operation failed"):
        super().__init__(message, code='appointment_error', status_code=status.HTTP_400_BAD_REQUEST)


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF that provides consistent error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize the response format
        custom_response_data = {
            'success': False,
            'error': {
                'code': getattr(exc, 'code', 'error'),
                'message': str(exc.detail) if hasattr(exc, 'detail') else str(exc),
                'status_code': response.status_code
            }
        }
        response.data = custom_response_data
    
    # Handle custom HMS exceptions
    if isinstance(exc, HMSAPIException):
        logger.error(f"HMS API Error: {exc.message}", exc_info=True)
        return Response(
            {
                'success': False,
                'error': {
                    'code': exc.code,
                    'message': exc.message,
                    'status_code': exc.status_code
                }
            },
            status=exc.status_code
        )
    
    # Log unhandled exceptions
    if response is None:
        logger.exception("Unhandled exception in API", exc_info=exc)
        return Response(
            {
                'success': False,
                'error': {
                    'code': 'internal_error',
                    'message': 'An internal error occurred',
                    'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return response
