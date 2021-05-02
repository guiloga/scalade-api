from typing import Type
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework import viewsets
from rest_framework import serializers

from api.exceptions import MethodNotAllowed
from common.utils import ModelManager


class UUIDLookupMixin:
    lookup_field = 'uuid'
    lookup_value_regex = '[0-9a-f-]{36}'


class BaseAPIViewSet(viewsets.ViewSet):
    def list(self, request):
        raise MethodNotAllowed()

    def create(self, request):
        raise MethodNotAllowed()

    def retrieve(self, request, uuid=None):
        raise MethodNotAllowed()

    def update(self, request, uuid=None):
        raise MethodNotAllowed()

    def destroy(self, request, uuid=None):
        raise MethodNotAllowed()
    

class BaseAPIViewSetSetMixin(UUIDLookupMixin):
    app_model_name: str = None

    @staticmethod
    def filter_paginated_results(request, query_set):
        limit, offset = (int(request.query_params.get('limit', 10)),
                         int(request.query_params.get('offset', 0)))
        items = query_set[offset:(offset+limit)]
        pagination_metadata = {
            'pagination': {
                'limit': limit,
                'offset': offset
            }
        }
        return items, pagination_metadata


class ListViewSetMixin(BaseAPIViewSetSetMixin):
    """
    Simple list ViewSet mixin without list filters params.
    """
    ListSerializer: Type[serializers.Serializer] = None

    def list(self, request):
        resources = ModelManager.handle(self.app_model_name, 'all')
        items, pg_metadata = self.filter_paginated_results(request, resources)

        list_serializer = self.ListSerializer(items, many=True, request=request)
        response_data = {
            'total_queryset': len(resources),
            'count': len(items),
            'data': list_serializer.data,
            'metadata': {
                **pg_metadata
            }
        }
        return Response(response_data,
                        status=HTTP_200_OK)


class RetrieveViewSetMixin(BaseAPIViewSetSetMixin):
    """
    Simple retrieve ViewSet mixin.
    """
    RetrieveSerializer: Type[serializers.Serializer] = None

    def retrieve(self, request, uuid=None):
        try:
            resource = ModelManager.handle(self.app_model_name, 'get', uuid=uuid)
        except ObjectDoesNotExist:
            raise NotFound(detail=f"resource identifier: '{uuid}' doesn't exist.")

        serializer = self.RetrieveSerializer(resource)
        return Response(
            serializer.data,
            status=HTTP_200_OK)


class ReadOnlyWithNoFiltersViewSetMixin(ListViewSetMixin, RetrieveViewSetMixin):
    """
    Read-only ViewSet with list and retrieve methods without listing filters.
    """
    pass
