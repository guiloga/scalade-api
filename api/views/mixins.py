from typing import Type, Tuple
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound, ParseError
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
    VALID_FILTERS: Tuple = None
    PAGINATION_FILTERS = ('limit', 'offset')

    def filter_paginated_results(self, request, queryset):
        limit, offset = (int(request.query_params.get(self.PAGINATION_FILTERS[0], 10)),
                         int(request.query_params.get(self.PAGINATION_FILTERS[1], 0)))
        items = queryset[offset:(offset+limit)]
        pagination_metadata = {
            'pagination': {
                'limit': limit,
                'offset': offset
            }
        }
        return items, pagination_metadata

    def apply_list_filters(self, request) -> Tuple:
        filters = self.build_filters(request)
        try:
            queryset = ModelManager.handle(
                self.app_model_name,
                'filter',
                **filters, )
            items, metadata = self.filter_paginated_results(request, queryset)
        except:
            self.raise_invalid_filters_error()

        metadata = dict(**metadata, **{'valid_filters': self.VALID_FILTERS})
        return len(queryset), items, metadata

    def build_filters(self, request) -> dict:
        filters = {}
        for key, value in request.query_params.items():
            self.check_filter(key)
            if key not in ['limit', 'offset']:
                filters[key] = value
        return filters

    def check_filter(self, filter):
        if filter not in self.PAGINATION_FILTERS and filter not in self.VALID_FILTERS:
            self.raise_invalid_filters_error()

    def raise_invalid_filters_error(self):
        raise ParseError(
            detail=f'Invalid query filters: valid ones are {self.VALID_FILTERS}')


class ListViewSetMixin(BaseAPIViewSetSetMixin):
    """
    Simple list ViewSet mixin filtering with all get params passed in the request.
    """
    ListSerializer: Type[serializers.Serializer] = None

    def list(self, request):
        total_queryset, items, metadata = self.apply_list_filters(request)
        list_serializer = self.ListSerializer(
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


class RetrieveViewSetMixin(BaseAPIViewSetSetMixin):
    """
    Simple retrieve ViewSet mixin.
    """
    RetrieveSerializer: Type[serializers.Serializer] = None

    def retrieve(self, request, uuid=None):
        try:
            resource = ModelManager.handle(
                self.app_model_name, 'get', uuid=uuid)
        except ObjectDoesNotExist:
            raise NotFound(
                detail=f"resource identifier: '{uuid}' doesn't exist.")

        serializer = self.RetrieveSerializer(resource)
        return Response(
            serializer.data,
            status=HTTP_200_OK)


class ReadOnlyWithNoFiltersViewSetMixin(ListViewSetMixin, RetrieveViewSetMixin):
    """
    Read-only ViewSet with list and retrieve methods without listing filters.
    """
    pass
