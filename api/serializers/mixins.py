from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.reverse import reverse

from common.utils import ModelManager


class BaseSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ListItemsWithURLSerializer(serializers.ModelSerializer):
    url_basename: str = None

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)

    def get_url(self, obj):
        return reverse(self.url_basename, args=[obj.uuid], request=self.request)


class UUIDFieldMixin(BaseSerializer):
    uuid = serializers.UUIDField()


class EmailValidatorMixin:
    def validate_email(self, email):
        try:
            ModelManager.handle(
                'accounts.account',
                'get',
                email=email)
            raise serializers.ValidationError(
                "'%s' already exist." % email)
        except ObjectDoesNotExist:
            return email
