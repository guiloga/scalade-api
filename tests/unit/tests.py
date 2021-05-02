import pytest
import requests_mock

from common.contracts import HttpClient
from common.api import KubernetesHttpClient, KubernetesAPI, BrickInstanceMessagesApi
from common.utils import ModelManager
from streams.models import FunctionTypeModel, FunctionInstanceModel, VariableModel


class TestModelManager:
    def test_get_model(self):
        ft_model = ModelManager.get_model('streams', 'functiontype')
        assert ft_model is FunctionTypeModel

        fi_model = ModelManager.get_model('streams', 'FunctionInstance')
        assert fi_model is FunctionInstanceModel

        var_model = ModelManager.get_model('streams', 'VariableModel')
        assert var_model is VariableModel


class TestKubernetesHttpClient:
    def test_creation(self):
        client = KubernetesHttpClient.new()
        assert issubclass(client.__class__, HttpClient)


class TestKubernetesAPI:
    @pytest.mark.usefixtures('k8s_api')
    def test_singleton(self, k8s_api):
        k8s_api_2 = KubernetesAPI()

        assert k8s_api == k8s_api_2
        assert k8s_api.client == k8s_api_2.client

    @pytest.mark.usefixtures('k8s_api')
    @pytest.mark.usefixture('k8s_resources')
    def test_create(self, k8s_api, k8s_resources):
        job_config = k8s_resources['job']
        with requests_mock.Mocker() as mocker:
            mocker.post(requests_mock.ANY,
                        json=job_config,
                        status_code=200)
            k8s_api.create('job', job_config)

    @pytest.mark.usefixtures('k8s_api')
    def test_retrieve(self, k8s_api):
        pass

    @pytest.mark.usefixtures('k8s_api')
    def test_update(self, k8s_api):
        pass

    @pytest.mark.usefixtures('k8s_api')
    def test_delete(self, k8s_api):
        pass


class TestBrickInstanceMessagesApi:
    def test_singleton(self):
        msg_api_1 = BrickInstanceMessagesApi()
        msg_api_2 = BrickInstanceMessagesApi()

        assert msg_api_1 == msg_api_2


class TestBrickInstanceMessagesRepository:
    def test_get_all_bi_uuid(self):
        pass
