import pickle

from rest_framework.permissions import AllowAny
from rest_framework.status import HTTP_200_OK, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.response import Response
from rest_framework.views import APIView
from scaladecore.utils import decode_b64str

from api.serializers.runtime import UpdateFIStatusSerializer, CreateFIOutputSerializer, \
    CreateFILogMessageSerializer
from common.exceptions import InconsistentStateChangeError
from common.utils import DecoratorShipper as Decorators
from common.utils import ModelManager
from streams.models import VariableModel


def _query_serialized_function_variables(function_instance, iot):
    variables = ModelManager.handle(
        'streams.variable',
        'filter',
        function_instance=function_instance,
        iot=iot)
    return [var_.to_entity.as_dict for var_ in variables]


class RetrieveFIContext(APIView):
    """
    Retrieves the runtime Context data of the underlying FunctionInstance.
    """
    permission_classes = [AllowAny]

    @Decorators.extract_fi_from_token
    def get(self, request):
        inputs = _query_serialized_function_variables(request.fi, 'input')
        outputs = _query_serialized_function_variables(request.fi, 'output')
        return Response(
            data={'function_instance': request.fi.to_entity.as_dict,
                  'inputs': inputs,
                  'outputs': outputs},
            status=HTTP_200_OK)


class CreateFILogMessage(APIView):
    """
    Creates a new log message related to the underlying FunctionInstance.
    """
    permission_classes = [AllowAny]

    @Decorators.extract_fi_from_token
    def post(self, request):
        serializer = CreateFILogMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        fi_log_message = ModelManager.handle(
            'streams.FunctionInstanceLogMessage',
            'create',
            function_instance=request.fi,
            log_message=serializer.validated_data['log_message'],
            log_level=serializer.validated_data['log_level'], )

        # TODO: Send changes trough a socket to application client

        return Response(status=HTTP_200_OK)


class UpdateFIStatus(APIView):
    """
    Updates the status of the underlying FunctionInstance.
    """
    permission_classes = [AllowAny]

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
            data={'function_instance': request.fi.to_entity.as_dict},
            status=HTTP_200_OK)


class CreateFIOutput(APIView):
    """
    Creates a new output Variable related to the underlying FunctionInstance.
    """
    permission_classes = [AllowAny]

    @Decorators.extract_fi_from_token
    def post(self, request):
        serializer = CreateFIOutputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            decoded_variable = pickle.loads(
                decode_b64str(serializer.validated_data['output']))
        except Exception as err:
            # TODO: Log that exception
            return Response(
                data={'error': 'A server error occurred while decoding base64 string.'},
                status=HTTP_500_INTERNAL_SERVER_ERROR)
        _, err_msg = VariableModel.create_output(
            fi_uuid=request.fi.uuid,
            output=decoded_variable)
        if err_msg:
            return Response(
                data={'error': err_msg},
                status=HTTP_409_CONFLICT)

        # TODO: Send changes trough a socket to application client

        outputs = _query_serialized_function_variables(request.fi, 'output')
        return Response(
            data={'outputs': outputs},
            status=HTTP_200_OK)
