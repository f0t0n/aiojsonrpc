class Inspector(object):
    def __init__(self):
        self._rpc_methods = {}

    @property
    def rpc_methods(self):
        if not self._rpc_methods:
            def is_rpc_method(method_name):
                return getattr(getattr(self, method_name),
                               'is_rpc_method', False)
            self._rpc_methods = {method_name for method_name in dir(self)
                                 if method_name != 'rpc_methods' and
                                 is_rpc_method(method_name)}
        return self._rpc_methods
