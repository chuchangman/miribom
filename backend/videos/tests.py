from rest_framework import status
from rest_framework.test import APITestCase

from products.models import Category, Product
from users.models import User
from .models import Like, Review, Video, VideoUpload


class PublicVideoReadPermissionTests(APITestCase):
    def setUp(self):
        user = User.objects.create(
            nickname='tester',
            profile_image_url='',
            housing_type='apartment',
        )
        category = Category.objects.create(
            name='TV',
            slug='tv',
            ai_label='tv',
            display_order=1,
        )
        product = Product.objects.create(
            category_id=category,
            product_id='test-product',
            title='Test Product',
            image='',
            link='',
        )
        video_upload = VideoUpload.objects.create(
            user_id=user,
            video_url='https://example.com/video.mp4',
            thumbnail_url='',
            status='uploaded',
        )
        self.video = Video.objects.create(
            video_upload_id=video_upload,
            product_id=product,
            user_id=user,
        )
        self.user = user
        Review.objects.create(
            video_id=self.video,
            user_id=user,
            rating=5,
            content='Test review',
        )

    def test_anonymous_user_can_list_videos(self):
        response = self.client.get('/api/videos/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data[0]['is_liked'])

    def test_authenticated_user_sees_liked_state_in_video_feed(self):
        Like.objects.create(user_id=self.user, video_id=self.video)
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/videos/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data[0]['is_liked'])

    def test_anonymous_user_cannot_create_video(self):
        response = self.client.post('/api/videos/', {}, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_user_can_list_reviews(self):
        response = self.client.get(f'/api/videos/{self.video.id}/reviews/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_user_cannot_create_review(self):
        response = self.client.post(
            f'/api/videos/{self.video.id}/reviews/',
            {'rating': 5, 'content': 'Review'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
