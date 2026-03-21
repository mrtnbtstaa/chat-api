from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken, TokenError
from channels.middleware import BaseMiddleware

class AuthTokenMiddleware(BaseMiddleware):

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        
        token = self.get_token_from_scope(scope)

        if not token:
            raise TokenError("Authorization token not provided")
        
        user_id = self.get_user_from_token(token)

        if not user_id:
            raise TokenError("No user id found")
        
        return await self.inner(scope, receive, send)

    def get_token_from_scope(self, scope):

        # Get the headers from the scope
        headers = dict(scope.get('headers', []))

        # Get the authorization from the header
        auth_header = headers.get(b"Authorization", b"").decode("utf-8")

        # If the authorization header exists and starts with Bearer return the token part
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header.split(" ")[1]

    @database_sync_to_async
    def get_user_from_token(self, token):
        access_token = AccessToken(token)
        return access_token["user_id"]