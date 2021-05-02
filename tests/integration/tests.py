from uuid import uuid4
import pytest
from scaladecore.entities import FunctionTypeEntity, StreamEntity, FunctionInstanceEntity, \
    VariableEntity, BrickInstanceMessageEntity
from scaladecore.variables import Variable
from common.utils import ModelManager
from common.api import BrickInstanceMessagesApi
from common.repositories import BrickInstanceMessagesRepository
from streams.models import VariableModel
import rpc.producer as rpc_client


@pytest.mark.django_db
def test_streams_models_relationships():
    streams = ModelManager.handle('streams.stream', 'all')
    st = streams[0]

    functions = st.functions.all()
    assert len(functions) > 0

    fi = functions[0]
    ft = fi.function_type
    instances = ft.instances.all()
    inst = instances[0]
    assert fi == inst

    vars = fi.variables.all()
    assert len(vars) > 0


class TestFunctionTypeModel:
    @pytest.mark.django_db
    def test_to_entity(self):
        func_types = ModelManager.handle('streams.functiontype', 'all')
        for ft in func_types:
            assert isinstance(ft.to_entity, FunctionTypeEntity)


class TestStreamModel:
    @pytest.mark.django_db
    def test_to_entity(self):
        streams = ModelManager.handle('streams.stream', 'all')
        for st in streams:
            assert isinstance(st.to_entity, StreamEntity)


class TestFunctionInstanceModel:
    @pytest.mark.django_db
    def test_to_entity(self):
        instances = ModelManager.handle('streams.functioninstance', 'all')
        for fi in instances:
            assert isinstance(fi.to_entity, FunctionInstanceEntity)


class TestVariableModel:
    @pytest.mark.django_db
    def test_to_entity(self):
        variables = ModelManager.handle('streams.variable', 'all')
        for cvar in variables:
            assert isinstance(cvar.to_entity, VariableEntity)

    @pytest.mark.django_db
    def test_create_output(self):
        fi = ModelManager.handle('streams.functioninstance', 'all')[0]
        output = Variable.create('text', 'output_1', 'My name is Foo and I love Bars')
        var_orm, _ = VariableModel.create_output(fi.uuid, output)
        assert var_orm.iot == 'output'
        assert var_orm.to_entity
        assert var_orm.rank == 0


class TestKubernetesAPI:
    @pytest.mark.usefixture('k8s_resources')
    @pytest.mark.usefixtures('k8s_api')
    def test_create_job(self, k8s_resources, k8s_api):
        job_config = {**k8s_resources['job']}
        id_ = uuid4()
        job_config['metadata']['name'] = f'{id_.hex[:8]}-' + job_config['metadata']['name']

        container_name = job_config['spec']['template']['spec']['containers'][0]['name']
        job_config['spec']['template']['spec']['containers'][0]['name'] = (
                f'{id_.hex[:8]}-' + container_name)

        response = k8s_api.create('job', job_config)
        assert response.status_code == 201


class TestBrickInstanceMessagesApi:
    @pytest.mark.usefixtures('bi_messages')
    def test_create(self, bi_messages):
        msg_api = BrickInstanceMessagesApi()
        for msg in bi_messages:
            _, ok, _ = msg_api.insert_one(msg)
            assert ok

    @pytest.mark.usefixtures('bi_messages')
    def test_select_all_by_bi_uuid(self, bi_messages):
        msg_api = BrickInstanceMessagesApi()
        bi_uuid = str(bi_messages[0].get('bi_uuid'))
        resp, ok, _ = msg_api.select_all_by_bi_uuid(bi_uuid=bi_uuid)

        assert len(resp['Items']) == len(bi_messages)
        assert ok


class TestBrickInstanceMessagesRepository:
    @pytest.mark.usefixtures('bi_messages')
    def test_get_all(self, bi_messages):
        repo = BrickInstanceMessagesRepository()
        bi_uuid = str(bi_messages[0].get('bi_uuid'))
        messages = repo.get_all(bi_uuid)

        for i in range(len(messages)):
            msg = messages[i]
            assert isinstance(msg, BrickInstanceMessageEntity)
            assert msg.as_dict == bi_messages[i].as_dict

        assert len(messages) == len(bi_messages)


class TestRpcConsumer:
    @pytest.mark.django_db
    def test_retrieve_bi(self):
        bi = self.get_bi()
        response = rpc_client.retrieve_bi(bi.uuid)
        assert not response.is_error and response.object['success']
        assert bi.to_entity.as_dict == response.object['bi_dict']
        inputs = [VariableEntity.create_from_dict(var_d)
                  for var_d in response.object['inputs_dict']]
        for it in inputs:
            assert isinstance(it, VariableEntity)

    @pytest.mark.django_db
    def test_add_bi_message(self):
        bi = self.get_bi()
        response = rpc_client.add_bi_message(bi.uuid, 'Message sent through RPC')
        assert not response.is_error and response.object['success']

    @pytest.mark.django_db
    def test_add_bi_message_error(self):
        bi = self.get_bi()
        response = rpc_client.add_bi_message(bi.uuid, None)
        assert response.is_error

    @pytest.mark.django_db
    def test_change_bi_status_blocked(self):
        bi = self._change_status('block')
        assert bi.get('status') == 'blocked'

    @pytest.mark.django_db
    def test_change_bi_status_completed(self):
        bi = self._change_status('complete')
        assert bi.get('status') == 'completed'

    @pytest.mark.django_db
    def test_create_bi_output(self):
        bi = self.get_running_bi()
        output = Variable.create('text', 'output_1', 'My name is Foo and I love Bars')
        response = rpc_client.create_bi_output(bi.uuid, output)
        assert not response.is_error and response.object['success']

    def _change_status(self, method_name: str) -> FunctionInstanceEntity:
        bi = self.get_running_bi()
        response = rpc_client.change_bi_status(bi.uuid, method_name)
        assert not response.is_error and response.object['success']

        bi = FunctionInstanceEntity.create_from_dict(
            response.object['bi_dict'])
        return bi

    @staticmethod
    def get_bi():
        return ModelManager.handle(
            'streams.functioninstance',
            'all').order_by('-created')[0]

    @staticmethod
    def get_running_bi():
        return ModelManager.handle(
            'streams.functioninstance',
            'filter',
            status='running').order_by('-created')[0]
