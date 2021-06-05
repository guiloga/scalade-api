from uuid import UUID, uuid4
import json
from typing import Tuple, Optional, Union

from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from scaladecore.entities import FunctionTypeEntity, StreamEntity, VariableEntity, \
    FunctionInstanceEntity, FunctionInstanceLogMessageEntity
from scaladecore.config import InputConfig, OutputConfig, PositionConfig
from scaladecore.variables import Variable

from common.contracts import ModelContract
from common.exceptions import InconsistentStateChangeError

# TODO: FunctionRepositoryModel (an Image container repository)


class FunctionTypeModel(ModelContract):
    uuid = models.UUIDField(primary_key=True,
                            default=uuid4,
                            editable=False,
                            verbose_name='Resource Identifier')
    key = models.CharField(max_length=50, unique=True)
    verbose_name = models.CharField(max_length=50)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    inputs = models.TextField(null=True)
    outputs = models.TextField(null=True)
    account = models.ForeignKey('accounts.AccountModel',
                                on_delete=models.CASCADE,
                                related_name='function_types',
                                help_text='The creator and owner of the function.')

    class Meta:
        ordering = ['-created', ]
        db_table = 'function_types'
        verbose_name = 'Function Type'

    @property
    def to_entity(self) -> FunctionTypeEntity:
        return FunctionTypeEntity(
            uuid=self.uuid,
            key=self.key,
            verbose_name=self.verbose_name,
            description=self.description,
            created=self.created,
            updated=self.updated,
            inputs=[InputConfig.deserialize(item)
                    for item in json.loads(self.inputs)] if self.inputs else None,
            outputs=[OutputConfig.deserialize(item)
                     for item in json.loads(self.outputs)] if self.outputs else None,
            account=self.account.to_entity, )

    def get_input_config(self, id_name):
        if not self.inputs:
            return None

        all_inputs = {item['id_name']: InputConfig.deserialize(item)
                      for item in json.loads(self.inputs)}
        return all_inputs[id_name]


class StreamModel(ModelContract):
    uuid = models.UUIDField(primary_key=True,
                            default=uuid4,
                            editable=False,
                            verbose_name='Resource Identifier')
    name = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    pushed = models.DateTimeField(null=True)
    updated = models.DateTimeField(auto_now=True)
    finished = models.DateTimeField(null=True)
    status = models.CharField(max_length=50, default=StreamEntity.STATUS[0][0],
                              choices=StreamEntity.STATUS)
    workspace = models.ForeignKey('accounts.WorkspaceModel',
                                  on_delete=models.CASCADE,
                                  related_name='streams',
                                  help_text='The Workspace that stream belongs to')
    account = models.ForeignKey('accounts.AccountModel',
                                on_delete=models.CASCADE,
                                related_name='streams',
                                help_text='The creator and owner of the stream.')

    class Meta:
        ordering = ['-created', ]
        db_table = 'streams'
        verbose_name = 'Stream'

    @property
    def to_entity(self) -> StreamEntity:
        return StreamEntity(
            uuid=self.uuid,
            name=self.name,
            created=self.created,
            pushed=self.pushed,
            updated=self.updated,
            finished=self.finished,
            status=self.status,
            account=self.account.to_entity, )

    def cancel(self):
        instances = self.functions.all()
        for inst in instances:
            inst.cancel()
        self.status = StreamEntity.STATUS[-2][0]
        self.save()


class FunctionInstanceModel(ModelContract):
    uuid = models.UUIDField(primary_key=True,
                            default=uuid4,
                            editable=False,
                            verbose_name='Resource Identifier')
    function_type = models.ForeignKey(FunctionTypeModel, on_delete=models.CASCADE,
                                      related_name='instances')
    stream = models.ForeignKey(StreamModel, on_delete=models.CASCADE,
                               related_name='functions')
    position = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    initialized = models.DateTimeField(null=True)
    updated = models.DateTimeField(auto_now=True)
    completed = models.DateTimeField(null=True)
    status = models.CharField(max_length=50, default=FunctionInstanceEntity.STATUS[0][0],
                              choices=FunctionInstanceEntity.STATUS)

    class Meta:
        ordering = ['-created', ]
        db_table = 'function_instances'
        verbose_name = 'Function Instance'

    @property
    def to_entity(self):
        return self.entity_class(
            uuid=self.uuid,
            function_type=self.function_type.to_entity,
            stream=self.stream.to_entity,
            position=PositionConfig.deserialize(json.loads(self.position)),
            created=self.created,
            initialized=self.initialized,
            updated=self.updated,
            completed=self.completed,
            status=self.status, )

    @property
    def entity_class(self):
        return FunctionInstanceEntity

    def cancel(self):
        self.status = self.entity_class.STATUS[-2][0]
        self.save()

    @property
    def is_running(self) -> bool:
        return self.status == self.entity_class.STATUS[1][0]

    def _block(self):
        if self.is_running:
            self.status = self.entity_class.STATUS[2][0]
            self.save()
        else:
            raise InconsistentStateChangeError(
                self.__class__,
                self.status,
                self.entity_class.STATUS[2][0])

    def _complete(self):
        if self.is_running:
            self.status = self.entity_class.STATUS[-1][0]
            self.save()
        else:
            raise InconsistentStateChangeError(
                self.__class__,
                self.status,
                self.entity_class.STATUS[-1][0])

    def update_status(self, status_method: str):
        mth = getattr(self, '_' + status_method)
        mth.__call__()


class VariableModel(ModelContract):
    uuid = models.UUIDField(primary_key=True,
                            default=uuid4,
                            editable=False,
                            verbose_name='Resource Identifier')
    created = models.DateTimeField(auto_now_add=True)
    iot = models.CharField(max_length=50, default='input', choices=[('input', 'INPUT'),
                                                                    ('output', 'OUTPUT'), ])
    id_name = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    charset = models.CharField(max_length=50, default='utf-8')
    bytes = models.BinaryField()
    function_instance = models.ForeignKey(FunctionInstanceModel, on_delete=models.CASCADE,
                                          related_name='variables')
    rank = models.IntegerField()

    class Meta:
        ordering = ['-created', ]
        db_table = 'variables'
        verbose_name = 'Variable'

    @property
    def to_entity(self) -> VariableEntity:
        return VariableEntity(
            uuid=self.uuid,
            created=self.created,
            iot=self.iot,
            id_name=self.id_name,
            type_=self.type,
            charset=self.charset,
            bytes_=self.bytes,
            fi_uuid=self.function_instance.uuid,
            rank=self.rank, )

    @classmethod
    def create_output(cls, fi_uuid: Union[UUID, str], output: Variable) -> Tuple[object, Optional[str]]:
        try:
            fi = FunctionInstanceModel.objects.get(uuid=fi_uuid)
        except ObjectDoesNotExist:
            return None, "function instance '%s' doesn't exist" % str(fi_uuid)
        try:
            last_output = cls.objects.filter(function_instance=fi, iot='output'
                                             ).order_by('-rank')[0]
            rank = last_output.rank + 1
        except IndexError:
            rank = 0
        variable = cls(
            iot='output',
            id_name=output.id_name,
            type=output.type,
            charset=output.charset,
            bytes=output.bytes,
            function_instance=fi,
            rank=rank)
        variable.save()
        return variable, None


class FunctionInstanceLogMessageModel(ModelContract):
    uuid = models.UUIDField(primary_key=True,
                            default=uuid4,
                            editable=False,
                            verbose_name='Resource Identifier')
    created = models.DateTimeField(auto_now_add=True)
    function_instance = models.ForeignKey(FunctionInstanceModel, on_delete=models.CASCADE,
                                          related_name='log_messages')
    log_message = models.CharField(max_length=500)
    log_level = models.CharField(max_length=50,
                                 choices=FunctionInstanceLogMessageEntity.LOG_LEVELS,
                                 default='info')

    class Meta:
        ordering = ['-created', ]
        db_table = 'function_instance_log_messages'
        verbose_name = 'Function Instance Log Message'

    @property
    def to_entity(self) -> FunctionInstanceLogMessageEntity:
        return FunctionInstanceLogMessageEntity(
            uuid=self.uuid,
            created=self.created,
            fi_uuid=self.function_instance.uuid,
            log_message=self.log_message,
            log_level=self.log_level, )
