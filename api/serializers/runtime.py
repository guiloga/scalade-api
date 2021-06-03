from rest_framework import serializers

from api.serializers import BaseSerializer
from scaladecore.entities import FunctionInstanceLogMessageEntity


class CreateFILogMessageSerializer(BaseSerializer):
    log_message = serializers.CharField(max_length=500)
    log_level = serializers.ChoiceField(
        choices=[level for level, _ in FunctionInstanceLogMessageEntity.LOG_LEVELS],
        default=FunctionInstanceLogMessageEntity.LOG_LEVELS[1][0],
        required=False)


class UpdateFIStatusSerializer(BaseSerializer):
    status_method = serializers.ChoiceField(choices=[('block', 'Block'),
                                                     ('complete', 'Complete')])


class CreateFIOutputSerializer(BaseSerializer):
    output = serializers.CharField()
