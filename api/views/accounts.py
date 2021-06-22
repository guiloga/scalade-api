from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ParseError
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED

from api.serializers.accounts import WorkspaceCreationSerializer, WorkspaceSerializer, \
    WorkspaceListSerializer, AccountSerializer, AccountListSerializer, BusinessSerializer, \
    BusinessListSerializer, UserSerializer, UserListSerializer
from common.utils import ModelManager
from common.utils import DecoratorShipper as Decorators
from api.views import BaseAPIViewSet
from api.views.mixins import ReadOnlyWithNoFiltersViewSetMixin, ListViewSetMixin, \
    RetrieveViewSetMixin


class WorkspaceViewSet(ListViewSetMixin, RetrieveViewSetMixin, BaseAPIViewSet):
    """
    API CRUD for Workspace, it implements: list, create and retrieve methods.
    """
    app_model_name = 'accounts.workspace'
    ListSerializer = WorkspaceListSerializer
    RetrieveSerializer = WorkspaceSerializer

    @Decorators.with_permission('accounts.view_workspacemodel')
    def list(self, request):
        return super().list(request)

    @Decorators.with_permission('accounts.add_workspacemodel')
    def create(self, request):
        creation_serializer = WorkspaceCreationSerializer(
            data=request.data)

        creation_serializer.is_valid(raise_exception=True)
        ws = creation_serializer.save()

        serializer = WorkspaceSerializer(ws)
        return Response(serializer.data,
                        status=HTTP_201_CREATED)

    @Decorators.with_permission('accounts.view_workspacemodel')
    def retrieve(self, request, uuid):
        return super().retrieve(request, uuid=uuid)


class AccountViewSet(RetrieveViewSetMixin, BaseAPIViewSet):
    """
    API CRUD for Account, it implements: list and retrieve methods.
    """
    app_model_name = 'accounts.account'
    RetrieveSerializer = AccountSerializer

    VALID_FILTERS = ('is_staff', 'is_active', 'related_to_workspace',)

    @Decorators.with_permission('accounts.view_accountmodel')
    def list(self, request):
        filters = {}
        initial_queryset = None
        for key, value in request.query_params.items():
            self.check_filter(key)
            if key not in ['limit', 'offset']:
                if key in ['is_staff', 'is_active']:
                    filters[key] = True if value == 'true' else False
                elif key == 'related_to_workspace':
                    workspace_uuid = request.query_params.get(
                        'related_to_workspace')
                    try:
                        workspace = ModelManager.handle(
                            'accounts.workspace',
                            'get',
                            uuid=workspace_uuid)
                    except ObjectDoesNotExist:
                        raise ParseError(
                            "Workspace '%s' doesn't exist." % workspace_uuid)
                    initial_queryset = workspace.accountmodel_set.all()

        if initial_queryset:
            accounts = initial_queryset.filter(**filters)
        else:
            accounts = ModelManager.handle(
                'accounts.account',
                'filter',
                **filters, )

        items, metadata = self.filter_paginated_results(request, accounts)
        list_serializer = AccountListSerializer(
            items, many=True, request=request)
        response_data = {
            'total_queryset': len(accounts),
            'count': len(items),
            'data': list_serializer.data,
            'metadata': {
                **metadata,
                **{'valid_filters': self.VALID_FILTERS}
            }
        }
        return Response(response_data,
                        status=HTTP_200_OK)

    @Decorators.with_permission('accounts.view_accountmodel')
    def retrieve(self, request, uuid):
        return super().retrieve(request, uuid=uuid)


class BusinessViewSetMixin(ReadOnlyWithNoFiltersViewSetMixin, BaseAPIViewSet):
    """
    API CRUD for Business, it implements: only list and retrieve methods without listing filters.
    """
    app_model_name = 'accounts.business'
    ListSerializer = BusinessListSerializer
    RetrieveSerializer = BusinessSerializer

    @Decorators.with_permission('accounts.view_businessmodel')
    def list(self, request):
        return super().list(request)

    @Decorators.with_permission('accounts.view_businessmodel')
    def retrieve(self, request, uuid):
        return super().retrieve(request, uuid=uuid)


class UserViewSetMixin(ReadOnlyWithNoFiltersViewSetMixin, BaseAPIViewSet):
    """
    API CRUD for User, it implements: only list and retrieve methods without listing filters.
    """
    app_model_name = 'accounts.user'
    ListSerializer = UserListSerializer
    RetrieveSerializer = UserSerializer

    @Decorators.with_permission('accounts.view_usermodel')
    def list(self, request):
        return super().list(request)

    @Decorators.with_permission('accounts.view_usermodel')
    def retrieve(self, request, uuid):
        return super().retrieve(request, uuid=uuid)
