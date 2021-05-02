from common.contracts import ApplicationHandler

from rpc.producers.function import run_function


class PushedStreamHandler(ApplicationHandler):
    @classmethod
    def handle(cls, stream_id: int):
        pass

