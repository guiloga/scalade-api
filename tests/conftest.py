from datetime import datetime
import glob
import json
import os
from uuid import uuid4

from faker import Faker
from model_bakery import baker
import pytest
from scaladecore.utils import get_foo_function_config
from scaladecore.variables import Variable
from scaladecore.entities import BrickInstanceMessageEntity
import yaml

from common.api import KubernetesAPI
from settings import RESOURCES_DIR

fake = Faker()


@pytest.fixture(scope='session', autouse=True)
def function_config():
    config = get_foo_function_config()
    return config


@pytest.fixture(autouse=True)
def django_db_setup(django_db_setup, django_db_blocker, function_config):
    with django_db_blocker.unblock():
        bs_account = baker.make(
            'accounts.AccountModel',
            uuid=uuid4(),
            auth_id=fake.simple_profile()['username'],
            username='test_business',
            email='business@fakecompany.org', )

        business = baker.make(
            'accounts.BusinessModel',
            uuid=uuid4(),
            master_account=bs_account,
            organization_name='Fake Company', )

        user_account = baker.make(
            'accounts.AccountModel',
            uuid=uuid4(),
            auth_id='{0}/{1}'.format(business.short_uuid, 'test_user'),
            username='test_user',
            email='test_user@fakecompany.org', )

        user = baker.make(
            'accounts.UserModel',
            uuid=uuid4(),
            account=user_account,
            business=business,
            first_name='User',
            last_name='Unit Tests', )

        function_type = baker.make(
            'streams.FunctionTypeModel',
            uuid=uuid4(),
            key=f'{user.short_uuid}/fake-function',
            verbose_name='Fake Function',
            description='Fake function description.',
            inputs=function_config.inputs_as_json,
            outputs=function_config.outputs_as_json,
            account=user_account, )

        stream = baker.make(
            'streams.StreamModel',
            uuid=uuid4(),
            name='FakeStream',
            account=user_account, )

        function_instance = baker.make(
            'streams.FunctionInstanceModel',
            uuid=uuid4(),
            function_type=function_type,
            stream=stream,
            position=json.dumps({'row': 0, 'col': 0}),
            status='running', )

        for pt in function_config.inputs:
            # we assume here text and datetime variables
            cvar = Variable.create(
                pt.type, pt.id_name,
                value=datetime.utcnow() if pt.type == 'datetime' else 'fakeValue')

            variable = baker.make(
                'streams.VariableModel',
                uuid=uuid4(),
                iot='input',
                id_name=cvar.id_name,
                type=cvar.type,
                charset=cvar.charset,
                bytes=cvar.bytes,
                function_instance=function_instance,
                rank=pt.rank, )


@pytest.fixture(scope='session')
def k8s_api():
    return KubernetesAPI()


@pytest.fixture(scope='session')
def k8s_resources():
    resources = dict()
    config_files = glob.glob(os.path.join(RESOURCES_DIR, 'k8s', '*.yml'))
    for filepath in config_files:
        with open(filepath, 'r') as file:
            name = os.path.basename(filepath).replace('.yml', '')
            resources[name] = yaml.safe_load(file)

    return resources


@pytest.fixture(scope='session')
def bi_messages():
    def brick_instance_messages_factory():
        fake_messages = ['Fake Message', 'Foo Bar',
                         'Hello my name is Foo', 'Brick is running', ]
        bi_uuid = uuid4()
        msg_list = []
        for msg in fake_messages:
            msg_list.append(BrickInstanceMessageEntity(
                uuid=uuid4(),
                created=datetime.utcnow(),
                bi_uuid=bi_uuid,
                message=msg, ))

        return msg_list

    return brick_instance_messages_factory()
