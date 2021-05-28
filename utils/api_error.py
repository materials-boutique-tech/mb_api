class APIError(Exception):
  def __init__(self, msg):
    self.msg = msg


class ApiError400(APIError):
  code = 400
  description = "Application Error"


class FormError(APIError):
  code = 422
  description = "Form Error"
