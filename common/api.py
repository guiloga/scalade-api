import logging

from .contracts import HttpClient, APIContract
from .utils import get_hex_string
from .mixins import BaseHeadersMixin
from settings import K8S_SERVER_URL, K8S_PORT, K8S_TOKEN, K8S_BASE_API_URL, K8S_NAMESPACE


class KubernetesHttpClient(BaseHeadersMixin, HttpClient):
    AUTH_HEADERS = {
        'Authorization': f'Bearer {K8S_TOKEN}',
        'Content-Type': 'application/json',
    }

    def __init__(self, namespace: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.namespace = namespace

    @classmethod
    def new(cls, server_url: str = K8S_SERVER_URL, port: int = K8S_PORT,
            base_api_url: str = K8S_BASE_API_URL, namespace: str = K8S_NAMESPACE):
        return cls(namespace, server_url, port, base_api_url, base_headers=cls.AUTH_HEADERS)

    def _refresh_token(self):
        # TODO: implement this method
        pass


class KubernetesAPI(APIContract):
    __inst = None
    LOGGERS = {
        'job': logging.getLogger('k8s_jobs'),
    }

    def __init__(self):
        self._client = KubernetesHttpClient.new()

    def __new__(cls):
        if not cls.__inst:
            cls.__inst = object.__new__(cls)
        return cls.__inst

    @property
    def client(self):
        return self._client

    def create(self, resource: str, config: dict):
        hex_id = get_hex_string()
        self._log_to(resource, 'info', '[%s] creating %s: %s' % (hex_id, resource, config))
        resp = self.client.post(relative_url=self._build_uri(config['apiVersion'], resource),
                                json=config,
                                verify=False)
        self._log_to(resource, 'info', '[%s] %s created' % (hex_id, resource))
        return resp

    def _log_to(self, resource_name, level, msg):
        logger = self.LOGGERS[resource_name]
        log_method = logger.__getattribute__(level)
        log_method(msg)

    def _build_uri(self, api_version, resource):
        return f"{api_version}/namespaces/{self.client.namespace}/{resource}s"
