from uuid import UUID
from typing import Tuple, Union

from django.core.exceptions import ObjectDoesNotExist
from guirpc.amqp.domain.objects import ProxyResponse
from guirpc.amqp.decorators import register_faas
from guirpc.amqp.serializers import JsonSerializer, BinarySerializer
from scaladecore.entities import BrickInstanceMessageEntity

from setup import django_apps_setup
# Required before accessing django apps
django_apps_setup()

from common.api import BrickInstanceMessagesApi
from common.utils import ModelManager
from streams.models import VariableModel


@register_faas(req_sz=JsonSerializer, resp_sz=JsonSerializer)
def retrieve_bi(x_request):
    """Retrieves a brick instance"""
    id_ = x_request.object['bi_uuid']
    try:
        bi = ModelManager.handle(
            'streams.functioninstance', 'get', uuid=id_)
    except ObjectDoesNotExist:
        return ProxyResponse(
            200, object_={'success': False,
                          'error': f'No brick instance found with uuid: {id_}'})
    bi_inputs = ModelManager.handle('streams.variable', 'filter', function_instance=bi)
    return ProxyResponse(
        200, object_={'success': True,
                      'bi_dict': bi.to_entity.as_dict,
                      'inputs_dict': [var_.to_entity.as_dict for var_ in bi_inputs]})


@register_faas(req_sz=JsonSerializer, resp_sz=JsonSerializer)
def add_bi_message(x_request):
    """Adds a new message into a brick instance"""
    def _validate(dt: dict) -> Tuple[bool, Union[str, None]]:
        if not isinstance(dt['bi_uuid'], str):
            return False, '"bi_uuid" field must be a str type'
        elif not isinstance(dt['message'], str):
            return False, '"message" field must be a str type'
        else:
            return True, None

    payload = {**x_request.object}
    valid, err_msg = _validate(payload)
    if not valid:
        return ProxyResponse(400, error_message=err_msg)

    bi_message = BrickInstanceMessageEntity(
        bi_uuid=UUID(payload['bi_uuid']),
        message=payload['message'])

    api = BrickInstanceMessagesApi()
    _, ok, err = api.insert_one(bi_message)
    if not ok:
        return ProxyResponse(
            200, object_={'success': False,
                          'error': 'A client error occurred on creating a '
                                   'BrickInstanceMessageEntity: %s' % err
                          })

    # TODO: Send changes trough a socket to application client
    return ProxyResponse(
        200, object_={'success': True})


@register_faas(req_sz=JsonSerializer, resp_sz=JsonSerializer)
def change_bi_status(x_request):
    """Updates a brick instance status"""
    def _validate(dt: dict) -> Tuple[bool, Union[str, None]]:
        if not isinstance(dt['bi_uuid'], str):
            return False, '"bi_uuid" field must be a str type'
        elif not isinstance(dt['status_method'], str):
            return False, '"status_method" field must be a str type'
        elif dt['status_method'] not in ['block', 'complete']:
            return False, '"status_method" value "%s" is invalid' % dt['status_method']
        else:
            return True, None

    payload = {**x_request.object}
    valid, err_msg = _validate(payload)
    if not valid:
        return ProxyResponse(400, error_message=err_msg)
    try:
        bi = ModelManager.handle(
            'streams.functioninstance',
            'get',
            uuid=payload['bi_uuid'])
        bi.update_status(payload['status_method'])
    except Exception as err:
        return ProxyResponse(
            200, object_={'success': False,
                          'error': 'An error occurred while changing status of '
                                   'bi #%s: %s' % (payload['bi_uuid'], err)
                          })

    # TODO: Send changes trough a socket to application client
    response = ProxyResponse(
        200, object_={'success': True, 'bi_dict': bi.to_entity.as_dict})

    return response


@register_faas(req_sz=BinarySerializer, resp_sz=BinarySerializer)
def create_bi_output(x_request):
    """Creates a new output into a brick instance"""
    bi_uuid = x_request.object['bi_uuid']
    output = x_request.object['output']
    _, err_msg = VariableModel.create_output(
        fi_uuid=bi_uuid,
        output=output, )
    if err_msg:
        return ProxyResponse(
            200, object_={'success': False,
                          'error': 'An error occurred while creating '
                                   'output variable: %s' % err_msg})

    # TODO: Send changes trough a socket to application client
    bi = ModelManager.handle(
        'streams.functioninstance',
        'get',
        uuid=bi_uuid)
    return ProxyResponse(
        200, object_={'success': True, 'bi_dict': bi.to_entity.as_dict})
