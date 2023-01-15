from werkzeug.exceptions import HTTPException

class AccessError(HTTPException):
    code = 403
    message = 'AccessError'

class InputError(HTTPException):
    code = 400
    message = 'InputError'
