from functools import partial
from . import factory

try:
    import ujson as json
except ImportError:
    import json


loads = partial(factory.loads, json)
dumps = partial(factory.dumps, json)
serialize = loads
deserialize = dumps
