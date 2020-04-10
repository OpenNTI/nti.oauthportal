class AuthorizationError(Exception):

    def __init__(self, error):
        super(AuthorizationError, self).__init__(error)
