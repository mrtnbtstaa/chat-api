from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthTokenMiddleware(BaseMiddleware):

    async def __call__(self, scope, receive, send):

        # Extract the token
        token = self.get_token_from_scope(scope)

        if token:
            try:
                user = await self.get_user_from_token(token)
                scope["user"] = user
            except Exception:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await self.inner(scope, receive, send)

    def get_token_from_scope(self, scope):

        # Get the headers from the scope
        headers = dict(scope.get('headers', []))

        # Get the authorization from the header
        auth_header = headers.get(b"authorization", b"").decode("utf-8")

        # If the authorization header exists and starts with Bearer return the token part
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header.split(" ")[1]
        
        return None

    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            access_token = AccessToken(token)
            return User.objects.get(id=access_token["user_id"])
        except Exception:
            return AnonymousUser()