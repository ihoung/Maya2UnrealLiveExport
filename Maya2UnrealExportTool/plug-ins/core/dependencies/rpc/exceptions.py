
class BaseRPCException(Exception):
    """
    Raised when a rpc class method is not authored as a static method.
    """
    def __init__(self, message=None, line_link=''):
        self.message = message + line_link
        # super().__init__(self.message)
        Exception.__init__(self, self.message)


class InvalidClassMethod(BaseRPCException):
    """
    Raised when a rpc class method is not authored as a static method.
    """
    def __init__(self, cls, method, message=None, line_link=''):
        self.message = message

        if message is None:
            self.message = (
                '\n  {0}.{1} is not a static method. Please decorate with @staticmethod.'.format(cls.__name__, method.__name__)
            )
        BaseRPCException.__init__(self, self.message, line_link)


class InvalidTestCasePort(BaseRPCException):
    """
    Raised when a rpc test case class does not have a port defined.
    """
    def __init__(self, cls, message=None, line_link=''):
        self.message = message

        if message is None:
            self.message = '\n  You must set {0}.port to a supported RPC port.'.format(cls.__name__)
        BaseRPCException.__init__(self, self.message, line_link)


class InvalidKeyWordParameters(BaseRPCException):
    """
    Raised when a rpc function has key word arguments in its parameters.
    """
    def __init__(self, function, kwargs, message=None, line_link=''):
        self.message = message

        if message is None:
            self.message = (
                    '\n  Keyword arguments "{0}" were found on "{1}". The RPC client does not '
                    'support key word arguments . Please change your code to use only arguments.'.format(kwargs, function.__name__)
                )
        BaseRPCException.__init__(self, self.message, line_link)


class UnsupportedArgumentType(BaseRPCException):
    """
    Raised when a rpc function's argument type is not supported.
    """
    def __init__(self, function, arg, supported_types, message=None, line_link=''):
        self.message = message

        if message is None:
            self.message = (
                '\n  "{0}" has an argument of type "{1}". The only types that are'
                ' supported by the RPC client are {2}.'.format(
                    function.__name__, arg.__class__.__name__, [supported_type.__name__ for supported_type in supported_types]
                )
            )
        BaseRPCException.__init__(self, self.message, line_link)


class FileNotSavedOnDisk(BaseRPCException):
    """
    Raised when a rpc function is called in a context where it is not a saved file on disk.
    """
    def __init__(self, function, message=None):
        self.message = message

        if message is None:
            self.message = (
                '\n  "{0}" is not being called from a saved file. The RPC client does not '
                'support code that is not saved. Please save your code to a file on disk and re-run it.'.format(function.__name__)
            )
        BaseRPCException.__init__(self, self.message)
