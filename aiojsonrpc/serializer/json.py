import ujson as json
from functools import partial
from . import factory


loads = partial(factory.loads, json)
dumps = partial(factory.dumps, json)
serialize = loads
deserialize = dumps
