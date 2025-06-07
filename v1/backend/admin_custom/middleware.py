from .signals import set_current_request

class RequestMiddleware:
    """Middleware to make request available in signals"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_request(request)
        response = self.get_response(request)
        return response
