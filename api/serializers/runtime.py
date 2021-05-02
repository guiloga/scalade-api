from rest_framework import serializers

from api.serializers import BaseSerializer
from api.serializers.mixins import UUIDFieldMixin


class GetFIContextSerializer(UUIDFieldMixin, BaseSerializer):
    pass


class CreateFILogMessageSerializer(UUIDFieldMixin, BaseSerializer):
    pass


class UpdateFIStatusSerializer(UUIDFieldMixin, BaseSerializer):
    pass


class CreateFIOutputSerializer(UUIDFieldMixin, BaseSerializer):
    pass
