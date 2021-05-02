from uuid import UUID

from guirpc.amqp.decorators import faas_producer
from guirpc.amqp.domain import ProxyRequest
from guirpc.amqp.serializers import JsonSerializer, BinarySerializer
from guirpc.amqp.utils import ClientConnector

from scaladecore.variables import Variable

CONNECTOR = ClientConnector()


@faas_producer(con=CONNECTOR, faas_name='retrieve_bi', req_sz=JsonSerializer)
def retrieve_bi(bi_uuid: UUID):
    payload = {'bi_uuid': str(bi_uuid), }
    return ProxyRequest(object_=payload)


@faas_producer(con=CONNECTOR, faas_name='add_bi_message', req_sz=JsonSerializer)
def add_bi_message(bi_uuid: UUID, message: str):
    payload = {
        'bi_uuid': str(bi_uuid),
        'message': message,
    }
    return ProxyRequest(object_=payload)


@faas_producer(con=CONNECTOR, faas_name='change_bi_status', req_sz=JsonSerializer)
def change_bi_status(bi_uuid: UUID, status: str):
    payload = {
        'bi_uuid': str(bi_uuid),
        'status_method': status,
    }
    return ProxyRequest(object_=payload)


@faas_producer(con=CONNECTOR, faas_name='create_bi_output', req_sz=BinarySerializer)
def create_bi_output(bi_uuid: str, output: Variable):
    object_ = {
        'bi_uuid': bi_uuid,
        'output': output,
    }
    return ProxyRequest(object_=object_)
