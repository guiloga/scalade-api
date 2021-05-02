from abc import ABC, abstractmethod
import logging
import requests
from typing import Type

from common.utils import get_hex_string
from django.db import models
from scaladecore.entities import EntityContract


class ModelContract(models.Model):
    uuid = None

    class Meta:
        abstract = True

    @property
    @abstractmethod
    def to_entity(self) -> EntityContract:
        pass

    @property
    def short_uuid(self):
        return str(self.uuid)[:8]


class ApplicationHandler(ABC):
    @classmethod
    @abstractmethod
    def handle(cls, stream_id: int):
        pass


class HttpClient(ABC):
    LOGGER = logging.getLogger('http_client')

    def __init__(self, server_url: str, port: int, base_api_url: str, base_headers: dict = None):
        self._server_url = server_url
        self._port = port
        self._base_api_url = base_api_url
        self._base_headers = base_headers

    @property
    def base_headers(self):
        return self._base_headers

    @classmethod
    @abstractmethod
    def new(cls, *args, **kwargs):
        pass

    def get(self, relative_url: str, url_params: dict = None, headers: dict = None, **kwargs):
        hex_id = get_hex_string()

        self._log_call(hex_id, 'GET', relative_url, url_params)
        response = requests.get(self._compose_url(relative_url),
                                params=url_params,
                                headers=headers,
                                **kwargs)

        self._log_response(hex_id, 'GET', response.status_code, response.json())
        return response

    def post(self, relative_url: str, body: dict = None, headers: dict = None, **kwargs):
        hex_id = get_hex_string()

        self._log_call(hex_id, 'POST', relative_url, body=body)
        response = requests.post(self._compose_url(relative_url),
                                 data=body,
                                 headers=headers,
                                 **kwargs)

        self._log_response(hex_id, 'POST', response.status_code, response.json())
        return response

    def put(self, relative_url: str, url_params: dict = None, body: dict = None, headers: dict = None, **kwargs):
        raise NotImplementedError

    def patch(self, relative_url: str, url_params: dict = None, body: dict = None, headers: dict = None, **kwargs):
        raise NotImplementedError

    def delete(self, relative_url: str, headers: dict = None, **kwargs):
        raise NotImplementedError

    def _compose_url(self, relative_url, append_slash=False):
        return "{0}/{1}/{2}{3}".format(
            self._server_url, self._base_api_url, relative_url, '/' if append_slash else '')

    def _log_call(self, hex_id, method, relative_url, url_params=None, body=None):
        self.LOGGER.info(f'[{hex_id}] HTTP CALL method: {method} | relative_url: {relative_url} | '
                         f'url_params: {url_params} | body: {body}')

    def _log_response(self, hex_id, method, status, response_body):
        self.LOGGER.info(f'[{hex_id}] HTTP RESPONSE method: {method} | status: {status} | '
                         f'body: {response_body}')


class APIContract(ABC):
    @abstractmethod
    def create(self, *args, **kwargs):
        pass

    @abstractmethod
    def retrieve(self, *args, **kwargs):
        pass

    @abstractmethod
    def update(self, *args, **kwargs):
        pass

    @abstractmethod
    def delete(self, *args, **kwargs):
        pass
