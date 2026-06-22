from rest_framework import status
from rest_framework.test import APITestCase

from .models import EmailUser, User


class MeViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            nickname='tester',
            profile_image_url='',
            housing_type='apartment',
            area_size=12,
        )
        EmailUser.objects.create(
            user_id=self.user,
            email='tester@example.com',
            password='hashed-password',
        )

    def test_me_returns_profile_fields(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/auth/me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.user.id)
        self.assertEqual(response.data['nickname'], 'tester')
        self.assertEqual(response.data['email'], 'tester@example.com')
        self.assertEqual(response.data['profile_image_url'], '')
        self.assertEqual(response.data['housing_type'], 'apartment')
        self.assertEqual(response.data['area_size'], 12)

    def test_me_patch_updates_nickname(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            '/api/auth/me/',
            {'nickname': 'updated-user'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nickname'], 'updated-user')
        self.user.refresh_from_db()
        self.assertEqual(self.user.nickname, 'updated-user')

    def test_me_patch_rejects_short_nickname(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            '/api/auth/me/',
            {'nickname': 'ab'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
