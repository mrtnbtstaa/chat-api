import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import OriginValidator
from .middleware.auth_token_middleware_stack import AuthTokenMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apps.config.settings.development')

django_asgi_app = get_asgi_application()

from apps.app_chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": OriginValidator(
        AuthTokenMiddleware(URLRouter(websocket_urlpatterns)),
        [
            
        ]
    )
})
