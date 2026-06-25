from rest_framework import status
from rest_framework.test import APITestCase

from products.models import Category, Product
from videos.models import Video, VideoUpload
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


class WithdrawalVideoCleanupTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(nickname='owner', profile_image_url='', housing_type='apartment')
        category = Category.objects.create(name='TV', slug='tv', ai_label='tv', display_order=1)
        product = Product.objects.create(
            category_id=category, product_id='p1', title='Test TV', image='', link=''
        )
        video_upload = VideoUpload.objects.create(
            user_id=self.user, video_url='https://example.com/v.mp4', thumbnail_url='', status='uploaded'
        )
        self.video = Video.objects.create(
            video_upload_id=video_upload, product_id=product, user_id=self.user
        )

    def test_withdrawal_soft_deletes_users_videos(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete('/api/auth/me/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.video.refresh_from_db()
        self.assertTrue(self.video.is_deleted)

    def test_withdrawal_does_not_delete_other_users_videos(self):
        other = User.objects.create(nickname='other', profile_image_url='', housing_type='apartment')
        category = Category.objects.get(slug='tv')
        product = Product.objects.get(product_id='p1')
        vu = VideoUpload.objects.create(
            user_id=other, video_url='https://example.com/v2.mp4', thumbnail_url='', status='uploaded'
        )
        other_video = Video.objects.create(video_upload_id=vu, product_id=product, user_id=other)

        self.client.force_authenticate(user=self.user)
        self.client.delete('/api/auth/me/')

        other_video.refresh_from_db()
        self.assertFalse(other_video.is_deleted)

    def test_withdrawal_removes_video_from_feed(self):
        self.client.force_authenticate(user=self.user)
        self.client.delete('/api/auth/me/')

        response = self.client.get('/api/videos/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
