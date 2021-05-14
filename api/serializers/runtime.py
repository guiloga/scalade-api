from rest_framework import serializers

from api.serializers import BaseSerializer


class CreateFILogMessageSerializer(BaseSerializer):
    pass


class UpdateFIStatusSerializer(BaseSerializer):
    status_method = serializers.ChoiceField(choices=[('block', 'Block'),
                                                     ('complete', 'Complete')])


class CreateFIOutputSerializer(BaseSerializer):
    pass
