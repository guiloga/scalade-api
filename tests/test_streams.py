from uuid import uuid4
import pytest
from scaladecore.entities import FunctionTypeEntity, StreamEntity, FunctionInstanceEntity, \
    VariableEntity
from scaladecore.variables import Variable
from common.utils import ModelManager
from streams.models import VariableModel


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


# TODO: Test accounts models
# TODO: Test FunctionInstanceLogMessageModel