from rest_framework.response import Response
from typing import Optional, Dict, Any, Type, List

def response_message(
    success: bool,
    message: str,
    errors: Optional[Dict[str, Any]] = None,
    data: Optional[Any] = None,
    status_code: int = 200
) -> Response:

    

    """
        Helper function to return json response

        Args:
            success (bool): data to be returned either true or false in the response
            message (str): Message of the error or success reponse
            data (Dict): Optional Additional data to be returned in the response,
            errors (Dict): Optional Additional data to be returned when error occured in response,
            status_code: (int): HTTP status code for the response

        Returns: Json Response with the given data
    """
    
    return Response({
        "success": success,
        "message": message,
        "data": data, # Will be null if not provided
        "errors": errors # Will be null if not provided
    }, status=status_code)





