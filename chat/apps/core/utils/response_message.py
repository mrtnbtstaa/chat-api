from rest_framework.response import Response
from typing import Optional, Any, List, Dict

def success_response(
    status: str,
    message: str,
    status_code: int = 200,
    data: Optional[Any] = None
) -> Response:
    
    return Response({
        "status": status,
        "message": message,
        "data": data,
    }, status=status_code)

def error_response(
    status: str,
    message: str,
    code: str,
    details: Optional[Any] = None,
    status_code: int = 400,
) -> Response:
    
    return Response({
        "status": status,
        "error": {
            "code": code,
            "message": message,
            "details": details
        }
    }, status=status_code)

def response_message(
    status: str,
    message: str,
    is_success: Optional[bool] = True,
    error_code: Optional[str] = "REQUEST DENIED",
    errors: Optional[List[Dict[str, Any]]] = None,
    data: Optional[Any] = None,
    status_code: Optional[int] = None
) -> Response:

    """
    Dispatcher helper to return either success or error response.
    """

    if is_success:
        sc = status_code or 200
        return success_response(
            status=status,
            message=message,
            data=data,
            status_code=sc
        )
    
    sc = status_code or 400
    return error_response(
        status=status,
        message=message,
        code=error_code,
        details=errors or [],
        status_code=sc
    )
    
    





