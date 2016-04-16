from .exception import RpcError
from .exception import RpcErrorCode


def rpc_method(method):
    method.is_rpc_method = True
    return method


def raise_method_not_found(method: str):
        raise RpcError('Method `{}` not found'.format(method),
                       RpcErrorCode.METHOD_NOT_FOUND)
