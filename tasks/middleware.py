# atlantis-shop/tasks/middleware.py

import json
from django.utils.deprecation import MiddlewareMixin

class SaveRequestBodyMiddleware(MiddlewareMixin):
    """Middleware для сохранения тела запроса для повторного чтения"""

    def process_request(self, request):
        # Сохраняем тело запроса для POST запросов с JSON
        if request.method == 'POST' and 'application/json' in request.content_type:
            # Читаем и сохраняем тело запроса
            request._body = request.body
            request._read_started = False
        return None