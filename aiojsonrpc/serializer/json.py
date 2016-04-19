from functools import partial
from . import factory


def import_ujson():
    import ujson
    return ujson


def import_json():
    try:
        json = import_ujson()
    except ImportError:
        import json
    return json


json = import_json()
loads = partial(factory.loads, json)
dumps = partial(factory.dumps, json)
serialize = loads
deserialize = dumps
