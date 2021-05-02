from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from api.serializers import BaseSerializer, ListItemsWithURLSerializer
from accounts.models import WorkspaceModel, AccountModel, BusinessModel, UserModel
from common.utils import ModelManager


class WorkspaceCreationSerializer(BaseSerializer):
    name = serializers.CharField(max_length=50)
    business = serializers.UUIDField()

    def create(self, validated_data):
        workspace = ModelManager.handle(
            'accounts.workspace',
            'create',
            name=validated_data['name'],
            business=validated_data['business'], )
        return workspace

    def validate_name(self, name):
        query = ModelManager.handle(
            'accounts.workspace',
            'filter',
            name=name,
            business__uuid=self.initial_data.get('business'))
        if len(query) > 0:
            raise serializers.ValidationError(
                "A workspace with that name '%s' already exists "
                "at the scope of the business." % name)
        return name

    def validate_business(self, business_uuid):
        try:
            business = ModelManager.handle('accounts.business', 'get', uuid=business_uuid)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                "Business is invalid: '%s' doesn't exist." % business_uuid)
        return business


class WorkspaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceModel
        fields = '__all__'


class WorkspaceListSerializer(ListItemsWithURLSerializer):
    url_basename = 'entities-api:workspaces-detail'
    url = serializers.SerializerMethodField()

    class Meta:
        model = WorkspaceModel
        fields = ['name', 'business', 'url']


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountModel
        exclude = ['password', ]


class AccountListSerializer(ListItemsWithURLSerializer):
    url_basename = 'entities-api:accounts-detail'
    url = serializers.SerializerMethodField()

    class Meta:
        model = AccountModel
        fields = ['uuid', 'created', 'auth_id', 'username', 'email', 'url']


class BusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessModel
        fields = '__all__'


class BusinessListSerializer(ListItemsWithURLSerializer):
    url_basename = 'entities-api:businesses-detail'
    url = serializers.SerializerMethodField()

    class Meta:
        model = BusinessModel
        fields = ['uuid', 'organization_name', 'url']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = '__all__'


class UserListSerializer(ListItemsWithURLSerializer):
    url_basename = 'entities-api:users-detail'
    url = serializers.SerializerMethodField()

    class Meta:
        model = UserModel
        fields = ['uuid', 'first_name', 'url']
