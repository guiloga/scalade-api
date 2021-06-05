from datetime import datetime
from django.core.management import call_command
import glob
import json
import os
from uuid import uuid4

from faker import Faker
from model_bakery import baker
import pytest
from scaladecore.utils import get_foo_function_config
from scaladecore.variables import Variable
import yaml

from common.api import KubernetesAPI
from settings import RESOURCES_DIR

fake = Faker()

JSON_FIXTURES = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'fixtures', 'all.json')


@pytest.fixture(scope='session', autouse=True)
def function_config():
    config = get_foo_function_config()
    return config


@pytest.fixture(autouse=True)
def django_db_setup(django_db_setup, django_db_blocker, function_config):
    with django_db_blocker.unblock():
        # the initial test DB is populated with json fixtures and
        # fake model instances baked by model_bakery.
        call_command('loaddata', JSON_FIXTURES)
        _bake_fixtures(function_config)


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


def _bake_fixtures(function_config):
    bs_account = baker.make(
        'accounts.AccountModel',
        uuid=uuid4(),
        auth_id=fake.simple_profile()['username'],
        username='test_business', )

    business = baker.make(
        'accounts.BusinessModel',
        uuid=uuid4(),
        master_account=bs_account,
        organization_name='Fake Company', )

    user_account = baker.make(
        'accounts.AccountModel',
        uuid=uuid4(),
        auth_id='{0}/{1}'.format(business.short_uuid, 'test_user'),
        username='test_user', )

    user = baker.make(
        'accounts.UserModel',
        uuid=uuid4(),
        account=user_account,
        business=business,
        first_name='User',
        last_name='Unit Tests', )

    workspace = baker.make(
        'accounts.WorkspaceModel',
        uuid=uuid4(),
        name='%s-%s' % (user.account.username, 'default'),
        business=business, )

    business.master_account.workspaces.add(workspace)
    user.account.workspaces.add(workspace)

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

    function_instance_log_message = baker.make(
        'streams.FunctionInstanceLogMessageModel',
        uuid=uuid4(),
        function_instance=function_instance,
        log_message='fake message', )

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
