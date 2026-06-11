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
        except TokenError:
            raise AuthenticationFailed('토큰이 만료되었거나 유효하지 않습니다.')

        try:
            user = User.objects.get(id=token['user_id'], is_deleted=False)
        except User.DoesNotExist:
            raise AuthenticationFailed('사용자를 찾을 수 없습니다.')

        return (user, token)
