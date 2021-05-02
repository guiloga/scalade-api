from rest_framework.status import HTTP_200_OK
from rest_framework.response import Response
from rest_framework.views import APIView


class GetFIContext(APIView):
    """
    Retrieves the runtime Context data of the underlying FunctionInstance.
    """
    def get(self, request):
        return Response(status=HTTP_200_OK)


class CreateFILogMessage(APIView):
    """
    Creates a new log message related to the underlying FunctionInstance.
    """
    def post(self, request):
        return Response(status=HTTP_200_OK)


class UpdateFIStatus(APIView):
    """
    Updates the status of the underlying FunctionInstance.
    """
    def patch(self, request):
        return Response(status=HTTP_200_OK)


class CreateFIOutput(APIView):
    """
    Creates a new output Variable related to the underlying FunctionInstance.
    """
    def post(self, request):
        return Response(status=HTTP_200_OK)
