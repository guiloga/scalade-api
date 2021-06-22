from typing import List, Dict

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
from scaladecore.utils import decode_b64str

from api.serializers.streams import FunctionTypeCreationSerializer, FunctionTypeListSerializer, \
    FunctionTypeSerializer, StreamCreationSerializer, StreamSerializer, StreamListSerializer, \
    FunctionInstanceCreationSerializer, FunctionInstanceSerializer, FunctionInstanceListSerializer, \
    VariableCreationSerializer, VariableSerializer, VariableListSerializer

from api.views import BaseAPIViewSet
from api.views.mixins import ListViewSetMixin, RetrieveViewSetMixin
from common.utils import ModelManager, validate_b64_encoded
from common.utils import DecoratorShipper as Decorators
from streams.models import FunctionInstanceModel


class FunctionTypeViewSet(RetrieveViewSetMixin, BaseAPIViewSet):
    """
    API CRUD for FunctionTypes, it implements: list, create and retrieve methods.
    """
    app_model_name = 'streams.functiontype'
    RetrieveSerializer = FunctionTypeSerializer

    VALID_FILTERS = ('username', 'key', )

    @Decorators.with_permission('streams.view_functiontypemodel')
    def list(self, request):
        total_queryset, items, metadata = self.apply_list_filters(request)
        list_serializer = FunctionTypeListSerializer(
            items, many=True, request=request)
        response_data = {
            'total_queryset': total_queryset,
            'count': len(items),
            'data': list_serializer.data,
            'metadata': {
                **metadata
            }
        }
        return Response(response_data,
                        status=HTTP_200_OK)

    @Decorators.with_permission('streams.add_functiontypemodel')
    def create(self, request):
        creation_serializer = FunctionTypeCreationSerializer(
            data={**request.data,
                  'key_prefix': request.user.short_uuid})

        creation_serializer.is_valid(raise_exception=True)
        ft = creation_serializer.save(account=request.user)

        serializer = FunctionTypeSerializer(ft)
        return Response(serializer.data,
                        status=HTTP_201_CREATED)

    @Decorators.with_permission('streams.view_functiontypemodel')
    def retrieve(self, request, uuid):
        return super().retrieve(request, uuid=uuid)

    def build_filters(self, request) -> dict:
        filters = {}
        for key, value in request.query_params.items():
            if key == 'username':
                filters['account__username'] = value
            else:
                if key not in ['limit', 'offset']:
                    filters[key] = value
        return filters


class StreamViewSet(RetrieveViewSetMixin, BaseAPIViewSet):
    """
    API CRUD for Stream, it implements: list, create and retrieve and destroy methods.
    """
    app_model_name = 'streams.stream'
    RetrieveSerializer = StreamSerializer

    VALID_FILTERS = ('username', 'name', 'status', 'status__in', )

    @Decorators.with_permission('streams.view_streammodel')
    def list(self, request):
        total_queryset, items, metadata = self.apply_list_filters(request)
        list_serializer = StreamListSerializer(
            items, many=True, request=request)
        response_data = {
            'total_queryset': total_queryset,
            'count': len(items),
            'data': list_serializer.data,
            'metadata': {
                **metadata
            }
        }
        return Response(response_data,
                        status=HTTP_200_OK)

    @Decorators.with_permission('streams.add_streammodel')
    def create(self, request):
        # TODO: Initial validation of function inputs (required ones and values for text, integer and datetime).
        stream_creation_serializer = StreamCreationSerializer(
            data={**request.data | {'account': request.user}})

        stream_creation_serializer.is_valid(raise_exception=True)
        stream = stream_creation_serializer.save(account=request.user)

        functions_data = request.data['spec'].get('functions', [])
        for fdt in functions_data:
            fdt.update({'stream': stream.uuid})

        func_inst_creation_serializer = FunctionInstanceCreationSerializer(data=functions_data,
                                                                           many=True)
        func_inst_creation_serializer.is_valid(raise_exception=False)
        if func_inst_creation_serializer.errors:
            stream.delete()
            for err in func_inst_creation_serializer.errors:
                if err:
                    raise ParseError(detail=err)

        instances = func_inst_creation_serializer.save()

        variables_data = try_create_input_variables(functions_data, instances)
        variable_creation_serializer = VariableCreationSerializer(data=variables_data,
                                                                  many=True)
        variable_creation_serializer.is_valid(raise_exception=False)
        if variable_creation_serializer.errors:
            for inst in instances:
                inst.delete()
            stream.delete()
            for err in variable_creation_serializer.errors:
                if err:
                    raise ParseError(detail=err)

        variables = variable_creation_serializer.save()

        stream_serializer = StreamSerializer(stream)
        return Response(stream_serializer.data,
                        status=HTTP_201_CREATED)

    @Decorators.with_permission('streams.view_streammodel')
    def retrieve(self, request, uuid):
        return super().retrieve(request, uuid=uuid)

    @Decorators.with_permission('streams.delete_streammodel')
    def destroy(self, request, uuid=None):
        try:
            st = ModelManager.handle(
                'streams.stream',
                'get',
                uuid=uuid, )
        except ObjectDoesNotExist:
            raise NotFound(
                detail=f"resource identifier: '{uuid}' doesn't exist.")

        st.cancel()

        serializer = StreamSerializer(st)
        return Response(serializer.data,
                        status=HTTP_200_OK)

    def build_filters(self, request) -> dict:
        filters = {}
        for key, value in request.query_params.items():
            if key == 'username':
                filters['user__username'] = value
            elif key == 'status__in':
                filters[key] = value.split(',')
            else:
                filters[key] = value
        return filters


class FunctionInstanceViewSet(RetrieveViewSetMixin, BaseAPIViewSet):
    """
    API CRUD for FunctionInstance, it implements: list and retrieve methods.
    """
    app_model_name = 'streams.functioninstance'
    RetrieveSerializer = FunctionInstanceSerializer

    VALID_FILTERS = ('function_type', 'stream', 'status', 'status__in')

    @Decorators.with_permission('streams.view_functioninstancemodel')
    def list(self, request):
        total_queryset, items, metadata = self.apply_list_filters(request)
        list_serializer = FunctionInstanceListSerializer(
            items, many=True, request=request)
        response_data = {
            'total_queryset': total_queryset,
            'count': len(items),
            'data': list_serializer.data,
            'metadata': {
                **metadata
            }
        }
        return Response(response_data,
                        status=HTTP_200_OK)

    @Decorators.with_permission('streams.view_functioninstancemodel')
    def retrieve(self, request, uuid):
        return super().retrieve(request, uuid=uuid)

    def build_filters(self, request) -> dict:
        filters = {}
        for key, value in request.query_params.items():
            if key == 'status__in':
                filters[key] = value.split(',')
            else:
                if key not in ['limit', 'offset']:
                    filters[key] = value
        return filters


class VariableViewSet(ListViewSetMixin, RetrieveViewSetMixin, BaseAPIViewSet):
    """
    API CRUD for Variable, it implements: list, retrieve and partial_update or patch methods.
    """
    app_model_name = 'streams.variable'
    ListSerializer = VariableListSerializer
    RetrieveSerializer = VariableSerializer

    VALID_FILTERS = ('iot', 'type', 'function_instance', )

    @Decorators.with_permission('streams.view_variablemodel')
    def list(self, request):
        return super().list(request)

    @Decorators.with_permission('streams.view_variablemodel')
    def retrieve(self, request, uuid):
        return super().retrieve(request, uuid=uuid)

    @Decorators.with_permission('streams.change_variablemodel')
    def partial_update(self, request, uuid=None):
        if 'body' not in request.data.keys():
            raise ParseError(
                detail={'body': 'field is required.'})
        else:
            body = request.data['body']
            if not body:
                raise ParseError(
                    detail={'body': 'field cannot be null.'})
            validate_b64_encoded(body)
        try:
            variable = ModelManager.handle(
                'streams.variable',
                'get',
                uuid=uuid, )
        except ObjectDoesNotExist:
            raise NotFound(
                detail=f"resource identifier: '{uuid}' doesn't exist.")

        variable.body = decode_b64str(body)
        variable.save()

        serializer = VariableSerializer(variable)
        return Response(serializer.data,
                        status=HTTP_200_OK)


def try_create_input_variables(funcs_data: dict,
                               func_instances: List[FunctionInstanceModel]
                               ) -> List[Dict]:
    input_variables = []
    for data, instance in zip(funcs_data, func_instances):
        for ivar in data.get('inputs', []):
            ivar['iot'] = 'input'

            if not ivar.get('id_name'):
                raise ParseError(
                    {'id_name': 'field is required for each input.'})
            try:
                input_config = instance.function_type.get_input_config(
                    ivar['id_name'])
            except KeyError:
                raise ParseError(
                    {'id_name': "'{0}' is not a valid input of function_type '{1}'".format(
                        ivar['id_name'], instance.function_type.uuid)
                     })

            ivar['type'] = input_config.type
            ivar['function_instance'] = instance.uuid
            ivar['rank'] = input_config.rank
            input_variables.append(ivar)

    return input_variables
