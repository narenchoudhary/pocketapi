from requests.exceptions import RequestException


class PocketException(RequestException):
    """Base Exception for PocketAPI"""
    pass


class PocketRequestError(PocketException):
    """Raised when request fails"""

    def __init__(self, status_code, x_error_code=None, x_error_msg=None):
        if status_code > 499:
            msg = "Pocket's sync server is down for scheduled maintenance"
        elif status_code == 403:
            msg = "User was authenticated, but access denied " \
                  "due to lack of permission or rate limiting"
        elif status_code == 401:
            msg = "Problem authenticating the user"
        elif status_code == 400:
            msg = " Invalid request, please make sure you follow " \
                  "the documentation for proper syntax"
        else:
            msg = "Unknown error occured."

        print('Status-Code: %d: %s' % (status_code, msg))
        if x_error_code and x_error_msg:
            print('X-Error-Code: %d: %s' % (x_error_code, x_error_msg))
        super(RequestException, self).__init__()
