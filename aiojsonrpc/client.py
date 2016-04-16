import os
import asyncio
import aiohttp
from itertools import count
from .constants import JSON_RPC_VERSION
from .serializer import json
from .serializer import msgpack
from .exception import RpcError


class Client(object):
    def __init__(self, service_url, data_type=str, id_iterator=None,
                 session_params={}):
        self._session_params = session_params
        self._data_type = data_type
        self._serializer = json if self._data_type is str else msgpack
        self._id_iterator = id_iterator or count(start=1, step=1)
        self._service_url = service_url

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(**self._session_params)
        self._ws = await self._session.ws_connect(self._service_url)
        self._send_request = (self._ws.send_str if self._data_type == str
                              else self._ws.send_bytes)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._ws.close()
        self._session.close()
        print('websocket connection closed')

    def create_request(self, method, **params):
        return self._serializer.dumps({
            'jsonrpc': JSON_RPC_VERSION,
            'method': method,
            'params': params,
            'id': next(self._id_iterator)
        })

    async def call(self, method, **params):
        self._send_request(self.create_request(method, **params))
        response = await self._ws.receive()
        data = self._serializer.loads(response.data)
        try:
            return data['result']
        except KeyError:
            raise RpcError(data['error']['message'], data['error']['code'])
