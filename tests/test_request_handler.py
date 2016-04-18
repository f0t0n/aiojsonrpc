import aiohttp
import asyncio
import pytest
from unittest import mock
from aiojsonrpc import request_handler
from aiojsonrpc.serializer import msgpack
from aiojsonrpc.serializer import json
from aiojsonrpc.service import Service
from aiojsonrpc.util import rpc_method
from aiojsonrpc.exception import RpcErrorCode


# def coro_mock(**kwargs):
#     return asyncio.coroutine(mock.Mock(**kwargs))

def coro_mock(**kwargs):
    coro = mock.Mock(**{**kwargs, 'name': 'coroutine_result'})
    corofn = mock.Mock(name='coroutine_function',
                       side_effect=asyncio.coroutine(coro))
    corofn.coro = coro
    return corofn


def result():
    return {
        'jsonrpc': '2.0',
        'result': 'test result',
        'id': 1
    }


def error(method):
    return {
            'jsonrpc': '2.0',
            'error': {
                'code': RpcErrorCode.METHOD_NOT_FOUND.value,
                'message': 'Method `{}` not found'.format(method),
            },
            'id': 1,
        }


def msg():
    def _msg(request):
        return request.param
    return _msg


def assert_send_bytes_called(ws, resp):
    assert not ws.send_str.called
    ws.send_bytes.assert_called_with(msgpack.dumps(resp))


def assert_send_str_called(ws, resp):
    assert not ws.send_bytes.called
    ws.send_str.assert_called_with(json.dumps(resp))


def create_request(service):
    return {
        'method': service,
        'params': {'foo': 'bar', 'answer': 42},
        'id': 1,
    }


def rpc_call():
    return create_request('TestService.test_method')


def rpc_call_non_rpc_method():
    return create_request('TestService.non_rpc_method')


def rpc_call_absent_method():
    return create_request('TestService.absent_method')


def rpc_call_absent_service():
    return create_request('AbsentService.test_method')


def rpc_call_invalid_method_param():
    return create_request('wrong_service_test_method')


def binary_rpc_call(get_source=rpc_call):
    return msgpack.dumps(get_source())


def text_rpc_call(get_source=rpc_call):
    return json.dumps(get_source())


def create_msg(tp, data, is_valid=True):
    msg = mock.MagicMock()
    msg.tp = tp
    msg.data = data
    try:
        msg.original_data = (msgpack if isinstance(data, bytes)
                             else json).loads(data)
    except (ValueError, TypeError):
        msg.original_data = data
    msg.is_valid = is_valid
    return msg


def valid_msg_params_binary():
    return [
        create_msg(aiohttp.MsgType.binary, binary_rpc_call()),
    ]


def valid_msg_params_text():
    return [
        create_msg(aiohttp.MsgType.text, text_rpc_call()),
    ]


def invalid_msg_params_binary():
    return [
        create_msg(aiohttp.MsgType.binary,
                   binary_rpc_call(get_source=source_fn),
                   is_valid=False)
        for source_fn in (rpc_call_non_rpc_method, rpc_call_absent_method,
                          rpc_call_absent_service,
                          rpc_call_invalid_method_param)
    ]


@pytest.fixture(scope='function')
def test_service():
    class TestService(Service):
        @rpc_method
        def test_method(self, foo='', answer=0):
            return 'test result'

        def non_rpc_method(self):
            pass
    return TestService


@pytest.fixture(scope='function')
def msg_handler():
    return request_handler.WebSocketMessageHandler()


@pytest.fixture(scope='function')
def rpc_websocket_handler():
    return request_handler.create_default_rpc_websocket_handler()


@pytest.fixture(scope='function')
def ws():
    ws = mock.MagicMock()
    ws.close = coro_mock(side_effect=Exception('websocket closed'))
    return ws


@pytest.fixture(scope='function')
def msg_close():
    return create_msg(aiohttp.MsgType.text, 'close')


@pytest.fixture(scope='function')
def msg_error():
    return create_msg(aiohttp.MsgType.error, None)


valid_msg_binary = pytest.fixture(scope='function',
                                  params=valid_msg_params_binary())(msg())
valid_msg_text = pytest.fixture(scope='function',
                                params=valid_msg_params_text())(msg())
invalid_msg_binary = pytest.fixture(scope='function',
                                    params=invalid_msg_params_binary())(msg())


@pytest.fixture(scope='function')
def services(test_service):
    return {test_service.__name__: test_service()}


@pytest.mark.asyncio
async def test_msg_handler_with_valid_msg_binary(msg_handler, ws,
                                                 valid_msg_binary, services):
    await msg_handler.handle_message(ws, valid_msg_binary, services)
    assert_send_bytes_called(ws, result())


@pytest.mark.asyncio
async def test_msg_handler_with_invalid_msg_binary(msg_handler, ws,
                                                   invalid_msg_binary,
                                                   services):
    await msg_handler.handle_message(ws, invalid_msg_binary, services)
    assert_send_bytes_called(ws,
                             error(invalid_msg_binary.original_data['method']))


@pytest.mark.asyncio
async def test_msg_handler_with_valid_msg_text(msg_handler, ws,
                                               valid_msg_text, services):
    await msg_handler.handle_message(ws, valid_msg_text, services)
    assert_send_str_called(ws, result())


@pytest.mark.asyncio
async def test_msg_handler_on_close(msg_handler, ws, msg_close, services):
    with pytest.raises(Exception) as e:
        await msg_handler.handle_message(ws, msg_close, services)
    assert str(e.value) == 'websocket closed'


@pytest.mark.asyncio
async def test_msg_handler_on_error(msg_handler, ws, msg_error, services):
    await msg_handler.handle_message(ws, msg_error, services)
    assert not ws.send_str.called
    assert not ws.send_bytes.called


def test_create_rpc_websocket_handler(test_service):
    req_handler = request_handler.create_rpc_websocket_handler(
        request_handler.WebSocketMessageHandler, services=[test_service])
    assert isinstance(req_handler, request_handler.RpcWebsocketHandler)


def test_create_default_rpc_websocket_handler(test_service):
    req_handler = request_handler.create_default_rpc_websocket_handler(
        services=[test_service])
    assert isinstance(req_handler, request_handler.RpcWebsocketHandler)


@pytest.mark.asyncio
@mock.patch('aiojsonrpc.request_handler.WebSocketMessageHandler')
async def test_rpc_websocket_handler(MockWebSocketMessageHandler):
    ws_response = 'aiojsonrpc.request_handler.WebSocketResponse'
    with mock.patch(ws_response) as MockWebSocketResponse:
        ws_msg_mock = mock.Mock()
        ws_msg_mock.tp = aiohttp.MsgType.close
        ws_instance = MockWebSocketResponse.return_value
        ws_instance.prepare = coro_mock()
        ws_instance.receive = coro_mock(return_value=ws_msg_mock)

        msg_handler = MockWebSocketMessageHandler.return_value
        msg_handler.handle_message = coro_mock()
        req = mock.MagicMock()

        await request_handler.RpcWebsocketHandler(msg_handler)(req)
        assert msg_handler.handle_message.called
