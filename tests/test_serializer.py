import json
import pytest
from aiojsonrpc.serializer import factory
from aiojsonrpc.serializer import json as json_serializer
from aiojsonrpc.serializer import msgpack as msgpack_serializer


@pytest.fixture(scope='function')
def serializers():
    return (json_serializer, msgpack_serializer, )


@pytest.fixture(scope='module')
def data_dict():
    return {'foo': 'bar', 'answer': 42}


@pytest.fixture(scope='module')
def data_str(data_dict):
    return json.dumps(data_dict)


def test_factory(data_dict, data_str):
    assert factory.dumps(json, data_dict) == data_str
    assert factory.loads(json, data_str) == data_dict


def test_serializers(serializers):
    for serializer in serializers:
        assert serializer.loads
        assert serializer.dumps
        assert serializer.serialize
        assert serializer.deserialize
