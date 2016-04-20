import asyncio
from unittest import mock


def coro_mock(**kwargs):
    coro = mock.Mock(**{**kwargs, 'name': 'coroutine_result'})
    corofn = mock.Mock(name='coroutine_function',
                       side_effect=asyncio.coroutine(coro))
    corofn.coro = coro
    return corofn
