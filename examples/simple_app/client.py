import asyncio
from aiojsonrpc.exception import RpcError
from aiojsonrpc.client import Client


SERVICE_URL = 'ws://127.0.0.1:8888/ws/json-rpc'


async def call(client, method, **params):
    try:
        print('-->', client.create_request(method, **params))
        res = await client.call(method, **params)
        print('<--', res)
        return res
    except RpcError as e:
        print('<-- Eh...', e.rpc_error_message)
        return 'Error {}: "{}"'.format(e.rpc_error_code, e.rpc_error_message)


async def call_aiojsonrpc_services():
    session_params = {
        'headers': {
            'Authorization': 'MyAuth <foo>:<bar>',
        },
    }
    async with Client(SERVICE_URL, data_type=bytes,
                      session_params=session_params) as client:
        await call(client, 'PrinterService.print', text='Letter')
        await call(client, 'CameraService.take_photo')
        await call(client, 'CameraService.take_photo')
        await call(client, 'PrinterService.get_firmware_version')

    async with Client(SERVICE_URL, data_type=str,
                      session_params=session_params) as client:
        await call(client, 'PrinterService.print', text='Title page')
        await call(client, 'CameraService.take_photo')
        await call(client, 'CameraService.non_existent_method')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(call_aiojsonrpc_services())
    loop.close()
