from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
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
            user = User.objects.get(id=token['user_id'])
        except (TokenError, User.DoesNotExist):
            raise AuthenticationFailed('유효하지 않은 토큰입니다.')

        return (user, token)
