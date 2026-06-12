from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import User


class CookieJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        access_token = request.COOKIES.get('access_token')
        if not access_token:
            return None

        try:
            token = AccessToken(access_token)
            user = User.objects.get(id=token['user_id'], is_deleted=False)
        except (TokenError, User.DoesNotExist):
            return None

        return (user, token)

    def authenticate_header(self, request):
        return 'Bearer realm="api"'
