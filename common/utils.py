import binascii
import os

from django.apps import apps
from rest_framework import serializers
from scaladecore.utils import BASE64_REGEX


class ModelManager:
    @classmethod
    def handle(cls, app_name_model: str, method: str, *args, **kwargs):
        app_name, model_name = app_name_model.split('.')
        model = cls.get_model(app_name, model_name)
        handler_method = getattr(model.objects, method)

        return handler_method(*args, **kwargs)

    @staticmethod
    def get_model(app_name: str, model_name: str):
        all_models = {model.__name__.lower(): model
                      for model in apps.get_app_config(app_name).get_models()}
        normalized_name = model_name.lower()
        suffix = 'model'
        if 'model' in normalized_name:
            suffix = ''
        return all_models[f'{normalized_name}{suffix}']


def validate_b64_encoded(body):
    if not BASE64_REGEX.search(body):
        raise serializers.ValidationError(
            f'must be bytes encoded in base64.')


def get_hex_string(size=12):
    return binascii.b2a_hex(os.urandom(size)).decode()


class DecoratorShipper:
    """
    Ships common used decorators as static methods.
    """
    @staticmethod
    def base_headers(func):
        def wrapper(inst, *args, **kwargs):
            hd_ = kwargs.get('headers', {})
            kwargs['headers'] = hd_ | inst.base_headers
            return func(inst, *args, **kwargs)

        return wrapper
