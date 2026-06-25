import requests
import os
from django.shortcuts import redirect as django_redirect
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema
from .models import User, SocialUser, EmailUser
from videos.models import Video
from .serializers import SignupSerializer, LoginSerializer, ProfileUpdateSerializer, PasswordChangeSerializer, LivingUpdateSerializer

FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
BACKEND_PUBLIC_URL = os.getenv('BACKEND_PUBLIC_URL', 'http://localhost:8000')
COOKIE_SECURE = os.getenv('COOKIE_SECURE', 'False') == 'True'


def _set_jwt_cookies(response, refresh):
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite='Lax',
        max_age=int(refresh.access_token.lifetime.total_seconds()),
    )
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite='Lax',
        max_age=int(refresh.lifetime.total_seconds()),
    )
    return response


def _issue_jwt(user):
    """이메일 로그인/회원가입용 — 쿠키만 설정, body에 토큰 없음"""
    refresh = RefreshToken.for_user(user)
    response = Response(status=status.HTTP_200_OK)
    return _set_jwt_cookies(response, refresh)


def _issue_jwt_redirect(user):
    """소셜 로그인 콜백용 — 쿠키 설정 후 프론트로 redirect"""
    refresh = RefreshToken.for_user(user)
    response = django_redirect(FRONTEND_URL)
    return _set_jwt_cookies(response, refresh)


def _get_or_create_social_user(provider, oauth_id, email, nickname):
    social_user = SocialUser.objects.filter(
        oauth_provider=provider,
        oauth_id=oauth_id
    ).first()

    if social_user:
        return social_user.user_id

    user = User.objects.create(nickname=nickname, is_deleted=False)
    SocialUser.objects.create(
        user_id=user,
        oauth_provider=provider,
        oauth_id=oauth_id,
        email=email,
    )
    return user


# ── 이메일 회원가입 / 로그인 ─────────────────────────────────────────────

class SignupView(APIView):
    authentication_classes = []

    @extend_schema(request=SignupSerializer, responses={200: None, 400: None, 409: None}, summary='이메일 회원가입')
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        email = data['email']

        if EmailUser.objects.filter(email=email).exists():
            return Response({'error': '이미 사용 중인 이메일입니다.'}, status=status.HTTP_409_CONFLICT)

        user = User.objects.create(nickname=data['nickname'], is_deleted=False)
        EmailUser.objects.create(
            user_id=user,
            email=email,
            password=make_password(data['password']),
        )
        return _issue_jwt(user)


class EmailLoginView(APIView):
    authentication_classes = []

    @extend_schema(request=LoginSerializer, responses={200: None, 400: None, 401: None}, summary='이메일 로그인')
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        email_user = EmailUser.objects.select_related('user_id').filter(email=data['email']).first()

        if not email_user or not check_password(data['password'], email_user.password):
            return Response(
                {'error': '이메일 또는 비밀번호가 올바르지 않습니다.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if email_user.user_id.is_deleted:
            return Response({'error': '탈퇴한 계정입니다.'}, status=status.HTTP_403_FORBIDDEN)

        return _issue_jwt(email_user.user_id)


# ── 로그아웃 / 토큰 갱신 ────────────────────────────────────────────────

class LogoutView(APIView):
    authentication_classes = []

    def post(self, request):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response


class CookieTokenRefreshView(APIView):
    authentication_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({'error': '리프레시 토큰이 없습니다.'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            refresh = RefreshToken(refresh_token)
        except TokenError:
            return Response({'error': '유효하지 않은 리프레시 토큰입니다.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not User.objects.filter(id=refresh['user_id'], is_deleted=False).exists():
            return Response({'error': '탈퇴한 사용자입니다.'}, status=status.HTTP_401_UNAUTHORIZED)

        response = Response(status=status.HTTP_200_OK)
        response.set_cookie(
            key='access_token',
            value=str(refresh.access_token),
            httponly=True,
            secure=COOKIE_SECURE,
            samesite='Lax',
            max_age=int(refresh.access_token.lifetime.total_seconds()),
        )
        return response


# ── 내 정보 조회 / 수정 / 탈퇴 ───────────────────────────────────────────

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_email(self, user):
        email_user = EmailUser.objects.filter(user_id=user).first()
        if email_user:
            return email_user.email

        social_user = SocialUser.objects.filter(user_id=user).first()
        if social_user:
            return social_user.email

        return ''

    def _serialize_user(self, user):
        return {
            'id': user.id,
            'nickname': user.nickname,
            'email': self._get_email(user),
            'profile_image_url': user.profile_image_url,
            'housing_type': user.housing_type,
            'area_size': user.area_size,
        }

    def get(self, request):
        return Response(self._serialize_user(request.user))

    @extend_schema(request=ProfileUpdateSerializer, responses={200: None, 400: None}, summary='내 프로필 수정')
    def patch(self, request):
        serializer = ProfileUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        data = serializer.validated_data
        if 'nickname' in data:
            user.nickname = data['nickname']
        if 'profile_image_url' in data:
            user.profile_image_url = data['profile_image_url']
        user.save(update_fields=list(data.keys()))

        return Response(self._serialize_user(user), status=status.HTTP_200_OK)

    @extend_schema(responses={204: None}, summary='회원 탈퇴')
    def delete(self, request):
        user = request.user
        user.is_deleted = True
        user.save(update_fields=['is_deleted'])
        Video.objects.filter(user_id=user, is_deleted=False).update(is_deleted=True)
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response


# ── 비밀번호 변경 ─────────────────────────────────────────────────────────

class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=PasswordChangeSerializer, responses={200: None, 400: None, 403: None}, summary='비밀번호 변경 (이메일 회원 전용)')
    def patch(self, request):
        email_user = EmailUser.objects.filter(user_id=request.user).first()
        if not email_user:
            return Response({'detail': '소셜 로그인 계정은 비밀번호를 변경할 수 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = PasswordChangeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        if not check_password(data['current_password'], email_user.password):
            return Response({'detail': '현재 비밀번호가 올바르지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)

        email_user.password = make_password(data['new_password'])
        email_user.save(update_fields=['password'])
        return Response(status=status.HTTP_200_OK)


# ── 생활 환경 조회 / 수정 ─────────────────────────────────────────────────

class LivingView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={200: None}, summary='생활 환경 조회')
    def get(self, request):
        user = request.user
        return Response({
            'housing_type': user.housing_type,
            'area_size': user.area_size,
            'living_updated_at': user.living_updated_at,
        })

    @extend_schema(request=LivingUpdateSerializer, responses={200: None}, summary='생활 환경 수정')
    def patch(self, request):
        serializer = LivingUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        data = serializer.validated_data
        if 'housing_type' in data:
            user.housing_type = data['housing_type']
        if 'area_size' in data:
            user.area_size = data['area_size']
        user.save(update_fields=[k for k in data.keys()])

        return Response({
            'housing_type': user.housing_type,
            'area_size': user.area_size,
            'living_updated_at': user.living_updated_at,
        })


# ── 네이버 ──────────────────────────────────────────────────────────────

class NaverLoginView(APIView):
    def get(self, request):
        client_id = os.getenv('NAVER_CLIENT_ID')
        redirect_uri = f'{BACKEND_PUBLIC_URL}/api/auth/naver/callback'
        naver_auth_url = (
            f"https://nid.naver.com/oauth2.0/authorize"
            f"?response_type=code"
            f"&client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&state=miribom"
        )
        return django_redirect(naver_auth_url)


class NaverCallbackView(APIView):
    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')

        token_res = requests.post(
            'https://nid.naver.com/oauth2.0/token',
            data={
                'grant_type': 'authorization_code',
                'client_id': os.getenv('NAVER_CLIENT_ID'),
                'client_secret': os.getenv('NAVER_CLIENT_SECRET'),
                'redirect_uri': f'{BACKEND_PUBLIC_URL}/api/auth/naver/callback',
                'code': code,
                'state': state,
            }
        )
        access_token = token_res.json().get('access_token')
        if not access_token:
            return Response({'error': '토큰 발급 실패'}, status=status.HTTP_400_BAD_REQUEST)

        user_res = requests.get(
            'https://openapi.naver.com/v1/nid/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        user_info = user_res.json().get('response')
        oauth_id = user_info.get('id')
        email = user_info.get('email', '')
        nickname = user_info.get('nickname', '네이버유저')

        user = _get_or_create_social_user('naver', oauth_id, email, nickname)
        return _issue_jwt_redirect(user)


# ── 카카오 ──────────────────────────────────────────────────────────────

class KakaoLoginView(APIView):
    def get(self, request):
        client_id = os.getenv('KAKAO_CLIENT_ID')
        redirect_uri = f'{BACKEND_PUBLIC_URL}/api/auth/kakao/callback'
        kakao_auth_url = (
            f"https://kauth.kakao.com/oauth/authorize"
            f"?response_type=code"
            f"&client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
        )
        return django_redirect(kakao_auth_url)


class KakaoCallbackView(APIView):
    def get(self, request):
        code = request.GET.get('code')

        token_res = requests.post(
            'https://kauth.kakao.com/oauth/token',
            data={
                'grant_type': 'authorization_code',
                'client_id': os.getenv('KAKAO_CLIENT_ID'),
                'client_secret': os.getenv('KAKAO_CLIENT_SECRET'),
                'redirect_uri': f'{BACKEND_PUBLIC_URL}/api/auth/kakao/callback',
                'code': code,
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
        )
        access_token = token_res.json().get('access_token')
        if not access_token:
            return Response({'error': '토큰 발급 실패'}, status=status.HTTP_400_BAD_REQUEST)

        user_res = requests.get(
            'https://kapi.kakao.com/v2/user/me',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        user_data = user_res.json()
        oauth_id = str(user_data.get('id'))
        kakao_account = user_data.get('kakao_account', {})
        email = kakao_account.get('email', '')
        nickname = kakao_account.get('profile', {}).get('nickname', '카카오유저')

        user = _get_or_create_social_user('kakao', oauth_id, email, nickname)
        return _issue_jwt_redirect(user)


# ── 구글 ────────────────────────────────────────────────────────────────

class GoogleLoginView(APIView):
    def get(self, request):
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        redirect_uri = f'{BACKEND_PUBLIC_URL}/api/auth/google/callback'
        google_auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth"
            f"?response_type=code"
            f"&client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope=openid+email+profile"
        )
        return django_redirect(google_auth_url)


class GoogleCallbackView(APIView):
    def get(self, request):
        code = request.GET.get('code')

        token_res = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'grant_type': 'authorization_code',
                'client_id': os.getenv('GOOGLE_CLIENT_ID'),
                'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
                'redirect_uri': f'{BACKEND_PUBLIC_URL}/api/auth/google/callback',
                'code': code,
            },
        )
        access_token = token_res.json().get('access_token')
        if not access_token:
            return Response({'error': '토큰 발급 실패'}, status=status.HTTP_400_BAD_REQUEST)

        user_res = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        user_info = user_res.json()
        oauth_id = user_info.get('sub')
        email = user_info.get('email', '')
        nickname = user_info.get('name', '구글유저')

        user = _get_or_create_social_user('google', oauth_id, email, nickname)
        return _issue_jwt_redirect(user)
