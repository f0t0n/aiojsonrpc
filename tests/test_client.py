import pytest
from aiojsonrpc.exception import RpcError
from aiojsonrpc.exception import RpcErrorCode
from aiojsonrpc.serializer import json
from aiojsonrpc.client import Client
from aiojsonrpc.request_handler import WebSocketMessageHandler
from tests.util import coro_mock
from collections import namedtuple
from functools import partial
from unittest import mock


def rpc_result_args():
    return 1, 42, json


def rpc_error_args():
    return 1, 'Method not found', RpcErrorCode.METHOD_NOT_FOUND, json


def ws_receive_result():
    return WebSocketMessageHandler().create_result(*rpc_result_args())


def ws_receive_error():
    return WebSocketMessageHandler().create_error(*rpc_error_args())


def msg(data):
    return namedtuple('Msg', 'data')(data=data)


msg_result = partial(msg, ws_receive_result())
msg_error = partial(msg, ws_receive_error())


@pytest.fixture(scope='function')
def mock_websocket_response():
    class MockWebSocketResponse():
        def __init__(self, res):
            self._res = res

        @property
        def is_error_response(self):
            try:
                json.loads(self._res.data)['result']
            except KeyError:
                return True
            else:
                return False

        async def receive(self):
            return self._res

        async def send_str(self, msg):
            pass

        async def send_bytes(self, msg):
            pass

        async def close(self):
            pass
    return MockWebSocketResponse


@pytest.fixture(scope='function', params=[msg_result(), msg_error()])
def ws_response(request, mock_websocket_response):
    return mock_websocket_response(request.param)


async def _make_call(client):
    return await client.call('TestService.test_method', foo='bar')


async def _on_error(client):
    with pytest.raises(RpcError) as e:
        await _make_call(client)
    _id, message, code, *_ = rpc_error_args()
    assert message in str(e)


async def _on_success(client):
    assert rpc_result_args()[1] == await _make_call(client)


@pytest.mark.asyncio
async def test_call(ws_response):
    with mock.patch('aiohttp.ClientSession') as MockClientSession:
        session_instance = MockClientSession.return_value
        session_instance.ws_connect = coro_mock(return_value=ws_response)
        async with Client('http://example.com/ws/rpc') as client:
            if ws_response.is_error_response:
                await _on_error(client)
            else:
                await _on_success(client)
