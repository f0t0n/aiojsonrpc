from unittest import mock
from aiojsonrpc.serializer.json import import_json


@mock.patch('aiojsonrpc.serializer.json.import_ujson', side_effect=ImportError)
def test_ujson_import_backoff(import_ujson_mock):
    import json
    assert import_json() == json


def test_ujson_import(request):
    import ujson
    assert import_json() == ujson
