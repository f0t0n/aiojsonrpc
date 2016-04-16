import asyncio
import pytest
from aiojsonrpc.exception import RpcError
from aiojsonrpc.service import Service
from aiojsonrpc.util import rpc_method


@pytest.fixture(scope='module')
def _service():

    class CustomService(Service):
        @rpc_method
        def meth(self, answer=0):
            return answer

        @rpc_method
        async def async_meth(self, foo=''):
            await asyncio.sleep(0.1)
            return foo

        def non_rpc_meth(self):
            pass

    return CustomService()


@pytest.mark.asyncio
async def test_call(_service):
    assert 42 == await _service('meth', answer=42)
    assert 'bar' == await _service('async_meth', foo='bar')
    with pytest.raises(RpcError) as e:
        await _service('non_rpc_meth')
    with pytest.raises(RpcError) as e:
        await _service('no_such_meth_at_all')
