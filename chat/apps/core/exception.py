from rest_framework.views import exception_handler
from apps.core.utils.response_message import response_message
from rest_framework.exceptions import Throttled, ParseError, AuthenticationFailed, NotAuthenticated, MethodNotAllowed, ValidationError
from rest_framework import status
from django.http import Http404


def custom_exception_handler(exc, context):

    if isinstance(exc, Http404):
        return response_message(
            is_success=False,
            status="error",
            message="The requested resource was not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            errors=[{
                "field": "resource",
                "issue": "does_not_exist"
            }]
        )

    if isinstance(exc, Throttled):
        return response_message(
            is_success=False,
            status="error",
            message="You are sending too many requests. Please try again later",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="THROTTLED",
            errors=[{
                "field": "rate_limit",
                "issue": f"Try again in {exc.wait} seconds"
            }]
        )
    
    if isinstance(exc, ParseError):
        return response_message(
            is_success=False,
            status="error",
            message="Invalid JSON format in request body",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="PARSE_ERROR",
            errors=[{
                "field": "body",
                "issue": "malformed_json"
            }]
        )
    
    if isinstance(exc, ValidationError):

        error_list = [
            {
                "field": field,
                "issue": str(messages[0])
            }
            for field, messages in exc.detail.items()
        ]

        return response_message(
            is_success=False,
            status="error",
            message="Validation Failed",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="BAD_REQUEST",
            errors=error_list
        )
    
    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        return response_message(
            is_success=False,
            status="error",
            message="Authentication credentials were not provided or invalid.",
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
            errors=[{
                "field": "auth",
                "issue": "missing_or_invalid_token"
            }]
        )
    
    if isinstance(exc, MethodNotAllowed):
        return response_message(
            is_success=False,
            status="error",
            message=f"The {context['request'].method} method is not allowed for this endpoint.",
            errors=[{
                "field": "method",
                "issue": f"Allowed: {exc.detail}"
            }],
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            error_code="METHOD_NOT_ALLOWED",
        )

    # Call DRF default exception handler first to get the error response
    response = exception_handler(exc, context)
    
    # Response has error
    if response and isinstance(response.data, dict):

        error_msg = response.data.get('detail', 'An unexpected error occurred on our end')

        if isinstance(response.data, dict) and 'detail' not in response.data:
            error_msg = "Validation failed."
        
        return response_message(
            is_success=False,
            status="error",
            message=error_msg,
            errors=[{
                "field": "server",
                "issue": "internal_error"
            }],
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_SERVER_ERROR"
        )

    import traceback
    traceback.print_exc()

    return response_message(
        is_success=False,
        status="error",
        message="A server error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
