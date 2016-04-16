from functools import partial
from . import factory
import msgpack


loads = partial(factory.loads, msgpack, encoding='utf-8')
dumps = partial(factory.dumps, msgpack, encoding='utf-8')
serialize = loads
deserialize = dumps
