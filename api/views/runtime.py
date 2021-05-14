from rest_framework.status import HTTP_200_OK, HTTP_409_CONFLICT
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.runtime import UpdateFIStatusSerializer
from common.exceptions import InconsistentStateChangeError
from common.utils import DecoratorShipper as Decorators
from common.utils import ModelManager


class GetFIContext(APIView):
    """
    Retrieves the runtime Context data of the underlying FunctionInstance.
    """
    @Decorators.extract_fi_from_token
    def get(self, request):
        inputs = ModelManager.handle(
            'streams.variable',
            'filter', function_instance=request.fi)
        return Response(
            data={'fi_dict': request.fi.to_entity.as_dict,
                  'inputs_dict': [var_.to_entity.as_dict for var_ in inputs]},
            status=HTTP_200_OK)


class CreateFILogMessage(APIView):
    """
    Creates a new log message related to the underlying FunctionInstance.
    """
    @Decorators.extract_fi_from_token
    def post(self, request):
        # TODO: Required refactor of FunctionInstance log messages before implementing this.
        return Response(status=HTTP_200_OK)


class UpdateFIStatus(APIView):
    """
    Updates the status of the underlying FunctionInstance.
    """
    @Decorators.extract_fi_from_token
    def patch(self, request):
        serializer = UpdateFIStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            request.fi.update_status(serializer.validated_data['status_method'])
        except InconsistentStateChangeError as exc:
            return Response(
                data={'error': 'Conflict with the current resource state. ' + str(exc)},
                status=HTTP_409_CONFLICT)

        # TODO: Maybe reduce body length: no need to re-serialize the function instance ?
        #       return only success or fail (consider also the 'updated' field).
        # TODO: Send changes trough a socket to application client

        return Response(
            data={'fi_dict': request.fi.to_entity.as_dict},
            status=HTTP_200_OK)


class CreateFIOutput(APIView):
    """
    Creates a new output Variable related to the underlying FunctionInstance.
    """
    @Decorators.extract_fi_from_token
    def post(self, request):
        return Response(status=HTTP_200_OK)
