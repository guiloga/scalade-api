import json

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from scaladecore.config import InputConfig
from scaladecore.utils import ID_NAME_REGEX, decode_b64str

from api.serializers import BaseSerializer, ListItemsWithURLSerializer
from streams.models import StreamModel, FunctionTypeModel, FunctionInstanceModel, VariableModel
from common.utils import ModelManager, validate_b64_encoded


class JSONStringField(serializers.Field):
    """
    A JSON String serialized to a dict primitive.
    """
    def to_representation(self, obj) -> dict:
        return json.loads(obj)

    def to_internal_value(self, data) -> str:
        return json.dumps(data)


class FunctionTypeCreationSerializer(BaseSerializer):
    """
    Function type creation serializer.
    """
    key = serializers.CharField(max_length=50)
    verbose_name = serializers.CharField(max_length=50)
    description = serializers.CharField(max_length=200)
    inputs = serializers.JSONField(encoder=json.JSONEncoder, allow_null=True)
    outputs = serializers.JSONField(encoder=json.JSONEncoder, allow_null=True)

    def create(self, validated_data):
        account = validated_data['account']
        function_type = ModelManager.handle(
            'streams.functiontype',
            'create',
            key=validated_data['key'],
            verbose_name=validated_data['verbose_name'],
            description=validated_data['description'],
            inputs=validated_data['inputs'],
            outputs=validated_data['outputs'],
            account=account, )

        return function_type

    def validate_inputs(self, inputs_data):
        if not inputs_data:
            return None

        configured_inputs = []
        for rk in range(len(inputs_data)):
            it = inputs_data[rk]
            try:
                input_config = InputConfig.deserialize(it | {'__rank__': rk})
                configured_inputs.append(input_config.serialize)
            except:
                raise serializers.ValidationError("'inputs' field error: "
                                                  f"{it} not validated.")
        return json.dumps(configured_inputs)

    def validate_outputs(self, outputs_data):
        if not outputs_data:
            return None

        configured_outputs = []
        for rk in range(len(outputs_data)):
            ot = outputs_data[rk]
            try:
                output_config = InputConfig.deserialize(ot | {'__rank__': rk})
                configured_outputs.append(output_config.serialize)
            except:
                raise serializers.ValidationError("'outputs' field error: "
                                                  f"{ot} not validated.")
        return json.dumps(configured_outputs)

    def validate(self, attrs):
        full_key = "{0}/{1}".format(
            self.initial_data['key_prefix'], attrs['key'])
        try:
            ft = FunctionTypeModel.objects.get(key=full_key)
        except ObjectDoesNotExist:
            ft = None
            attrs['key'] = full_key
        if ft:
            raise serializers.ValidationError({'key': f"'{full_key}' is already in use, "
                                                      "it must be unique."})

        return attrs


class FunctionTypeSerializer(serializers.ModelSerializer):
    """
    Function type detail serializer.
    """
    inputs = JSONStringField(allow_null=True, required=False)
    outputs = JSONStringField(allow_null=True, required=False)

    class Meta:
        model = FunctionTypeModel
        fields = '__all__'


class FunctionTypeListSerializer(ListItemsWithURLSerializer):
    url_basename = 'entities-api:function_types-detail'
    url = serializers.SerializerMethodField()

    class Meta:
        model = FunctionTypeModel
        fields = ['uuid', 'key', 'verbose_name', 'description', 'url']


class VariableCreationSerializer(BaseSerializer):
    """
    VariableModel creation serializer.
    """
    iot = serializers.CharField()
    id_name = serializers.CharField(max_length=50)
    type = serializers.CharField()
    charset = serializers.CharField(required=False, default='utf-8')
    bytes = serializers.CharField()
    function_instance = serializers.UUIDField()
    rank = serializers.IntegerField()

    def create(self, validated_data):
        variable = ModelManager.handle(
            'streams.variable',
            'create',
            iot=validated_data['iot'],
            id_name=validated_data['id_name'],
            type=validated_data['type'],
            charset=validated_data['charset'],
            bytes=validated_data['bytes'],
            function_instance=validated_data['function_instance'],
            rank=validated_data['rank'], )

        return variable

    def update(self, instance, validated_data):
        raise NotImplementedError

    def validate_id_name(self, id_name):
        if not ID_NAME_REGEX.search(id_name):
            raise serializers.ValidationError(
                f'cannot contain special characters. It has to match: {ID_NAME_REGEX}')
        return id_name

    def validate_function_instance(self, ft_uuid):
        try:
            func_type = ModelManager.handle('streams.functioninstance', 'get', uuid=ft_uuid)
        except ObjectDoesNotExist:
            raise uuid_validation_error(ft_uuid)

        return func_type

    def validate(self, attrs):
        b64_bytes = attrs['bytes']
        validate_b64_encoded(b64_bytes)

        attrs['bytes'] = decode_b64str(b64_bytes)
        return attrs


class VariableSerializer(serializers.ModelSerializer):
    """
    VariableModel detail serializer.
    """
    class Meta:
        model = VariableModel
        fields = '__all__'


class VariableListSerializer(ListItemsWithURLSerializer):
    """
    VariableModel list serializer.
    """
    url_basename = 'entities-api:variables-detail'
    url = serializers.SerializerMethodField()

    class Meta:
        model = VariableModel
        fields = ['uuid', 'created', 'iot', 'type', 'function_instance', 'url']


class FunctionInstanceCreationSerializer(BaseSerializer):
    """
    Function instance creation serializer.
    """
    type = serializers.UUIDField()
    stream = serializers.UUIDField()
    position = serializers.JSONField(encoder=json.JSONEncoder)

    def create(self, validated_data):
        function_instance = ModelManager.handle(
            'streams.functioninstance',
            'create',
            function_type=validated_data['type'],
            stream=validated_data['stream'],
            position=validated_data['position'], )

        return function_instance

    def update(self, instance, validated_data):
        raise NotImplementedError

    def validate_type(self, ft_uuid):
        try:
            func_type = ModelManager.handle('streams.functiontype', 'get', uuid=ft_uuid)
        except ObjectDoesNotExist:
            raise uuid_validation_error(ft_uuid)

        return func_type

    def validate_stream(self, stream_uuid):
        try:
            stream = ModelManager.handle('streams.stream', 'get', uuid=stream_uuid)
        except ObjectDoesNotExist:
            raise uuid_validation_error(stream_uuid)

        return stream

    def validate_position(self, position):
        if ['row', 'col'] != list(position.keys()):
            raise serializers.ValidationError(
                "Required position fields are 'row' and 'col'")

        return json.dumps(position)


class FunctionInstanceSerializer(serializers.ModelSerializer):
    """
    Function instance with related variables serializer.
    """
    inputs = serializers.SerializerMethodField()
    outputs = serializers.SerializerMethodField()
    position = JSONStringField()

    class Meta:
        model = FunctionInstanceModel
        fields = '__all__'

    def get_inputs(self, obj):
        return self._serialize_io_variables(obj, 'input')

    def get_outputs(self, obj):
        return self._serialize_io_variables(obj, 'output')

    def _serialize_io_variables(self, obj, iot: str):
        variables = obj.variables.filter(iot=iot)
        serializer = VariableSerializer(variables, many=True)
        return serializer.data


class FunctionInstanceListSerializer(ListItemsWithURLSerializer):
    """
    Function instance reduced detail serializer.
    """
    url_basename = 'entities-api:function_instances-detail'
    url = serializers.SerializerMethodField()

    class Meta:
        model = FunctionInstanceModel
        fields = ['uuid', 'function_type', 'stream', 'updated', 'status', 'url']


class StreamSpecSerializer(BaseSerializer):
    name = serializers.CharField(max_length=50)
    functions = serializers.ListField(required=False)

    def validate_name(self, name):
        if len(name) < 4:
            raise serializers.ValidationError('requires a minimum length of 4 characters.')
        return name


class StreamMetadataSerializer(BaseSerializer):
    workspace = serializers.CharField(max_length=50)


class StreamCreationSerializer(BaseSerializer):
    """
    StreamModel creation serializer.
    """
    spec = StreamSpecSerializer()
    metadata = StreamMetadataSerializer()

    def create(self, validated_data):
        stream = ModelManager.handle(
            'streams.stream',
            'create',
            name=validated_data['name'],
            account=validated_data['account'],
            workspace=validated_data['workspace'],
        )

        return stream

    def update(self, instance, validated_data):
        raise NotImplementedError

    def validate(self, attrs):
        account = self.initial_data['account']
        ws_name = attrs['metadata'].get('workspace')
        if not ws_name:
            raise serializers.ValidationError('a valid workspace is not provided.')

        try:
            workspace = [ws for ws in account.workspaces.all()
                         if ws.name == ws_name][0]
        except IndexError:
            raise PermissionDenied(detail=f'workspace "{ws_name}" permission denied.')

        attrs['spec']['workspace'] = workspace
        return attrs['spec']


class StreamSerializer(serializers.ModelSerializer):
    """
    StreamModel detail serializer.
    """
    functions = serializers.SerializerMethodField()

    class Meta:
        model = StreamModel
        fields = '__all__'

    def get_functions(self, obj):
        serializer = FunctionInstanceSerializer(obj.functions.all(), many=True)
        return serializer.data

    @property
    def data(self):
        sd = super().data
        for fc in sd['functions']:
            inputs_ = fc['inputs']
            for ipt in inputs_:
                ipt['__rank__'] = ipt.pop('rank')
            inputs_.sort(key=lambda x: x['__rank__'])

            outputs_ = fc['outputs']
            for ipt in outputs_:
                ipt['__rank__'] = ipt.pop('rank')
            outputs_.sort(key=lambda x: x['__rank__'])

        return sd


class StreamListSerializer(ListItemsWithURLSerializer):
    """
    StreamModel list serializer.
    """
    url_basename = 'entities-api:streams-detail'
    account = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = StreamModel
        fields = ['uuid', 'name', 'updated', 'status', 'account', 'url']

    def get_account(self, obj):
        return obj.account.uuid


def uuid_validation_error(res_uuid):
    return serializers.ValidationError(detail=
        f"'{res_uuid}' resource identifier not found")

