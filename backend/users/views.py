import requests
import os
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Social_User


def _get_or_create_social_user(provider, oauth_id, email, nickname):
    social_user = Social_User.objects.filter(
        oauth_provider=provider,
        oauth_id=oauth_id
    ).first()

    if social_user:
        return social_user.user_id

    user = User.objects.create(nickname=nickname, is_deleted=False)
    Social_User.objects.create(
        user_id=user,
        oauth_provider=provider,
        oauth_id=oauth_id,
        email=email,
    )
    return user


def _issue_jwt(user):
    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    })


# ── 네이버 ──────────────────────────────────────────────────────────────

class NaverLoginView(APIView):
    def get(self, request):
        client_id = os.getenv('NAVER_CLIENT_ID')
        redirect_uri = 'http://localhost:8000/api/auth/naver/callback'
        naver_auth_url = (
            f"https://nid.naver.com/oauth2.0/authorize"
            f"?response_type=code"
            f"&client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&state=miribom"
        )
        return redirect(naver_auth_url)


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
                'redirect_uri': 'http://localhost:8000/api/auth/naver/callback',
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
        return _issue_jwt(user)


# ── 카카오 ──────────────────────────────────────────────────────────────

class KakaoLoginView(APIView):
    def get(self, request):
        client_id = os.getenv('KAKAO_CLIENT_ID')
        redirect_uri = 'http://localhost:8000/api/auth/kakao/callback'
        kakao_auth_url = (
            f"https://kauth.kakao.com/oauth/authorize"
            f"?response_type=code"
            f"&client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
        )
        return redirect(kakao_auth_url)


class KakaoCallbackView(APIView):
    def get(self, request):
        code = request.GET.get('code')

        token_res = requests.post(
            'https://kauth.kakao.com/oauth/token',
            data={
                'grant_type': 'authorization_code',
                'client_id': os.getenv('KAKAO_CLIENT_ID'),
                'client_secret': os.getenv('KAKAO_CLIENT_SECRET'),
                'redirect_uri': 'http://localhost:8000/api/auth/kakao/callback',
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
        return _issue_jwt(user)


# ── 구글 ────────────────────────────────────────────────────────────────

class GoogleLoginView(APIView):
    def get(self, request):
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        redirect_uri = 'http://localhost:8000/api/auth/google/callback'
        google_auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth"
            f"?response_type=code"
            f"&client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope=openid+email+profile"
        )
        return redirect(google_auth_url)


class GoogleCallbackView(APIView):
    def get(self, request):
        code = request.GET.get('code')

        token_res = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'grant_type': 'authorization_code',
                'client_id': os.getenv('GOOGLE_CLIENT_ID'),
                'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
                'redirect_uri': 'http://localhost:8000/api/auth/google/callback',
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
        return _issue_jwt(user)