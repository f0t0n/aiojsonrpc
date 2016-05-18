import aiohttp
from aiohttp.web import WebSocketResponse
from .exception import RpcError
from .exception import RpcErrorCode
from .serializer import json
from .serializer import msgpack
from .constants import JSON_RPC_VERSION
from .util import raise_method_not_found


class WebSocketMessageHandler(object):
    def __init__(self, bytes_serializer=msgpack, str_serializer=json):
        self.set_bytes_serializer(bytes_serializer)
        self.set_str_serializer(str_serializer)

    async def handle_message(self, ws, msg, services):
        if msg.tp == aiohttp.MsgType.text:
            if msg.data == 'close':
                await ws.close()
            else:
                ws.send_str(await self._call_service(services, msg.data,
                                                     self._str_serializer))
        elif msg.tp == aiohttp.MsgType.binary:
            ws.send_bytes(await self._call_service(services, msg.data,
                                                   self._bytes_serializer))
        elif msg.tp == aiohttp.MsgType.error:
            print('ws connection closed '
                  'with exception {}'.format(ws.exception()))
        return ws

    def set_bytes_serializer(self, serializer):
        self._bytes_serializer = serializer

    def set_str_serializer(self, serializer):
        self._str_serializer = serializer

    def parse_request(self, data, serializer):
        request = serializer.loads(data)
        return request['method'], request['params'], request['id']

    def create_result(self, id, result, serializer):
        return serializer.dumps({
            'jsonrpc': JSON_RPC_VERSION,
            'result': result,
            'id': id,
        })

    def create_error(self, id, message, code, serializer):
        return serializer.dumps({
            'jsonrpc': JSON_RPC_VERSION,
            'error': {
                'code': code.value,
                'message': message,
            },
            'id': id,
        })

    async def _call_service(self, services, data, serializer):
        method, params, id = self.parse_request(data, serializer)
        try:
            try:
                service_name, method_name = method.split('.')
            except ValueError as e:
                raise_method_not_found(method)
            try:
                service_instance = services[service_name]
            except KeyError:
                raise_method_not_found(method)
            result = await service_instance(method_name, **params)
            return self.create_result(id, result, serializer)
        except RpcError as e:
            return self.create_error(id, e.rpc_error_message,
                                     e.rpc_error_code, serializer)


class RpcWebsocketHandler(object):
    def __init__(self, ws_msg_handler, services=None):
        self._ws_msg_handler = ws_msg_handler or WebSocketMessageHandler()
        self._services = {}
        try:
            self.register_services(services)
        except TypeError:
            pass

    async def __call__(self, request):
        self._request = request
        ws = WebSocketResponse()
        await ws.prepare(request)
        await self._save_websocket(ws)
        try:
            await self._handle_ws(ws)
        finally:
            await self._remove_websocket(ws)
        print('websocket connection closed')
        return ws

    def register_services(self, services):
        for service in services:
            self.register_service(service)

    def register_service(self, service):
        self._services[service.__name__] = service
        return self._services

    async def _save_websocket(self, ws):
        self._request.app['websockets'].append(ws)

    async def _remove_websocket(self, ws):
        self._request.app['websockets'].remove(ws)

    def _create_context(self, request, **context) -> dict:
        return {**request.get('_context', {}), **context}

    def _get_services(self, **context):
        return {name: cls(**context) for name, cls in self._services.items()}

    async def _handle_ws(self, ws):
        context = self._create_context(self._request)
        _services = self._get_services(**context)
        async for msg in ws:
            await self._ws_msg_handler.handle_message(ws, msg, _services)
        return ws


def create_rpc_websocket_handler(ws_msg_handler, services=None):
    return RpcWebsocketHandler(ws_msg_handler, services=services)


def create_default_rpc_websocket_handler(services=None):
    return create_rpc_websocket_handler(WebSocketMessageHandler(),
                                        services=services)
