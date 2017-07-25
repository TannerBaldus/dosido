class HelpScoutApiException(Exception):
    pass

class ResourceNotFound(HelpScoutApiException):

    def __init__(self, message, status_code, *args):
        self.message = message
        # allow users initialize misc. arguments as any other builtin Error
        super(MyAppValueError, self).__init__(message, foo, *args)
