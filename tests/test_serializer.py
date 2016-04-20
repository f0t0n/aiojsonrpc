import json
import msgpack
import pytest
from aiojsonrpc.serializer import factory
from aiojsonrpc.serializer import json as json_serializer
from aiojsonrpc.serializer import msgpack as msgpack_serializer


@pytest.fixture(scope='function', params=[json_serializer, msgpack_serializer])
def serializer(request):
    return request.param


@pytest.fixture(scope='function')
def data_dict():
    return {'foo': 'bar', 'answer': 42}


@pytest.fixture(scope='function')
def data_str(data_dict):
    return json.dumps(data_dict)


@pytest.fixture(scope='function')
def data_bytes(data_dict):
    return msgpack.dumps(data_dict, encoding='utf-8')


def test_factory(data_dict, data_str, data_bytes):
    assert factory.dumps(json, data_dict) == data_str
    assert factory.loads(json, data_str) == data_dict
    assert factory.dumps(msgpack, data_dict, encoding='utf-8') == data_bytes
    assert factory.loads(msgpack, data_bytes, encoding='utf-8') == data_dict


def test_serializers(serializer):
    assert serializer.loads
    assert serializer.dumps
    assert serializer.serialize
    assert serializer.deserialize
