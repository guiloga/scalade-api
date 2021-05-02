import logging
from decimal import Decimal
from typing import Tuple

from boto3 import resource as b3_resource
from boto3.dynamodb.conditions import Key
from boto3.resources.base import ServiceResource
from botocore.exceptions import ClientError

from .contracts import HttpClient
from .utils import get_hex_string
from .mixins import BaseHeadersMixin, BaseAPIMixin
from settings import K8S_SERVER_URL, K8S_PORT, K8S_TOKEN, K8S_BASE_API_URL, K8S_NAMESPACE, \
    AWS_REGION_NAME, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, DDB_BIMSG_TABLE


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


class KubernetesAPI(BaseAPIMixin):
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


class BrickInstanceMessagesApi:
    __inst = None

    def __init__(self):
        self._db = b3_resource('dynamodb',
                               region_name=AWS_REGION_NAME,
                               aws_access_key_id=AWS_ACCESS_KEY_ID,
                               aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        self._set_table()

    def __new__(cls):
        if not cls.__inst:
            cls.__inst = object.__new__(cls)
        return cls.__inst

    @property
    def db(self) -> ServiceResource:
        return self._db

    @property
    def table(self):
        return self._table

    def _set_table(self):
        self._table = self._db.Table(DDB_BIMSG_TABLE)

    def insert_one(self, bi_msg):
        """Inserts a new brick instance message"""
        item = bi_msg.as_dict
        item['created'] = Decimal(str(item['created']))
        try:
            response = self.table.put_item(Item=item)
        except ClientError as err:
            return err.response['Error']['Message'], False

        return self.eval_response(response)

    def select_all_by_bi_uuid(self, bi_uuid, **filters):
        # TODO: Handle paginated query results
        response = self.table.query(
            KeyConditionExpression=Key('bi_uuid').eq(bi_uuid),
        )
        return self.eval_response(response)

    @staticmethod
    def eval_response(resp: dict) -> Tuple[dict, bool, str]:
        st_code = resp['ResponseMetadata']['HTTPStatusCode']
        ok = st_code == 200
        return resp, ok, "No error message; status_code = %s" % st_code
