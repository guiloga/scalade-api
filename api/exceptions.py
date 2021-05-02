from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_405_METHOD_NOT_ALLOWED


class MethodNotAllowed(APIException):
    status_code = HTTP_405_METHOD_NOT_ALLOWED
    default_code = 'method_not_allowed'
    default_detail = 'Method not allowed for this resource.'
