import asyncio
from .util import raise_method_not_found


class Service(object):
    """ Base RPC service impolementation.
    Example of usage:

    ```python
    from aiojsonrpc.service import Service
    from aiojsonrpc.service_mixin import Inspector
    from aiojsonrpc.util import rpc_method


    class HelloWorldService(Service, Inspector):
        @rpc_method
        async def hello_world(self, x=0, y=0):
            return 'Hello world, x: {}, y: {}'.format(x, y)

        @rpc_method
        def foo_bar(self):
            return 'foo bar'

        def non_rpc_method(self):
            pass
    ```
    """
    def __init__(self, **context):
        self.context = context

    async def __call__(self, method, **params):
        try:
            fn = getattr(self, method)
            assert fn.is_rpc_method
        except (AttributeError, AssertionError) as e:
            raise_method_not_found('{}.{}'.format(self.__class__.__name__,
                                                  method))
        result = (await fn(**params)
                  if asyncio.iscoroutinefunction(fn)
                  else fn(**params))
        return result
