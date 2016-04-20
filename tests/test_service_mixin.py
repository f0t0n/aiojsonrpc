import pytest
from aiojsonrpc.service_mixin import Inspector
from aiojsonrpc.util import rpc_method
from unittest import mock


@pytest.fixture(scope='function')
def service():
    class Service(Inspector):
        @rpc_method
        def rpc_method(self):
            pass

        def non_rpc_method(self):
            pass
    return Service()


def test_inspector(service):
    assert 'rpc_method' in service.rpc_methods
    assert 'non_rpc_method' not in service.rpc_methods
    assert 'non_existing_method' not in service.rpc_methods
