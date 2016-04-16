import asyncio
from aiohttp import web
from aiojsonrpc.service import Service
from aiojsonrpc.request_handler import create_default_rpc_websocket_handler
from aiojsonrpc.util import rpc_method
from random import SystemRandom
from uuid import uuid4


class PrinterService(Service):
    @rpc_method
    def print(self, text=''):
        return 'Text `{}` has been printed'.format(text)

    def get_firmware_version(self):
        return '3.1.459'


class CameraService(Service):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rnd = SystemRandom()

    @rpc_method
    async def take_photo(self):
        return 'Picture `{}` has been taken.'.format(await self.save_photo())

    async def save_photo(self):
        await asyncio.sleep(self._rnd.randint(500, 1000) / 1000)
        return '{}.bmp'.format(uuid4().hex)


def create_app():
    services = (PrinterService, CameraService, )
    ws_handler = create_default_rpc_websocket_handler(services=services)
    app = web.Application()
    app['websockets'] = []
    app.router.add_route('GET', '/ws/json-rpc', ws_handler)
    return app


if __name__ == '__main__':
    web.run_app(create_app(), port=8888)
