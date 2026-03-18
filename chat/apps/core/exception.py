from rest_framework.views import exception_handler
from .utils import response_message
from rest_framework.exceptions import Throttled, ParseError, AuthenticationFailed, NotAuthenticated, MethodNotAllowed, ValidationError
from rest_framework import status
from django.http import Http404


def custom_exception_handler(exc, context):

    if isinstance(exc, Http404):
        return response_message(
            success=False,
            message="The requested resource was not found",
            status_code=status.HTTP_404_NOT_FOUND
        )

    if isinstance(exc, Throttled):
        return response_message(
            success=False,
            message="You are sending too many requests. Please try again later",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    if isinstance(exc, ParseError):
        return response_message(
            success=False,
            message="Invalid JSON format in request body",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    if isinstance(exc, ValidationError):
        return response_message(
            success=False,
            message=exc.detail,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        return response_message(
            success=False,
            message="Authentication credentials were not provided or invalid.",
            status_code=status.HTTP_401_UNAUTHORIZED
        )
    
    if isinstance(exc, MethodNotAllowed):
        return response_message(
            success=False,
            message=f"The {context['request'].method} method is not allowed for this endpoint.",
            errors={"allowed_methods": exc.detail},
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    # Call DRF default exception handler first to get the error response
    response = exception_handler(exc, context)
    
    # Response has error
    if response and isinstance(response.data, dict):

        error_msg = response.data.get('detail', 'An error occurred.')

        if isinstance(response.data, dict) and 'detail' not in response.data:
            error_msg = "Validation failed."
        
        return response_message(
            success=False,
            message=error_msg,
            errors=response.data,
            status_code=response.status_code
        )

    import traceback
    traceback.print_exc()

    return response_message(
        success=False,
        message="A server error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
