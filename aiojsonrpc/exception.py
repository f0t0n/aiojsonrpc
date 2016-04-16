from enum import Enum


class RpcErrorCode(Enum):
    """ JSON-RPC 2.0 error codes:

        -32700  Parse error Invalid JSON was received by the server.
            - An error occurred on the server while parsing the JSON text.
        -32600  Invalid Request
            - The JSON sent is not a valid Request object.
        -32601  Method not found
            - The method does not exist / is not available.
        -32602  Invalid params
            - Invalid method parameter(s).
        -32603  Internal error
            - Internal JSON-RPC error.
        -32000 to -32099    Server error
            - Reserved for implementation-defined server-errors.

        Ref.: http://www.jsonrpc.org/specification#error_object
    """
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603


class RpcError(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.rpc_error_message = message
        self.rpc_error_code = code
