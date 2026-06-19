from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, Product


class ProductPaginationTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='청소기',
            slug='vacuum',
            ai_label='vacuum',
            display_order=1,
        )
        Product.objects.bulk_create(
            [
                Product(
                    category_id=self.category,
                    product_id=f'product-{index}',
                    title=f'테스트 제품 {index:02d}',
                    brand='테스트 브랜드',
                    image='https://example.com/product.jpg',
                    lprice=index,
                    link='https://example.com/product',
                )
                for index in range(45)
            ]
        )

    def test_product_list_returns_40_products_and_next_offset(self):
        response = self.client.get(
            '/api/products/',
            {'limit': 40, 'offset': 0},
            HTTP_HOST='localhost',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 40)
        self.assertEqual(response.data['next_offset'], 40)
        self.assertTrue(response.data['has_next'])

    def test_product_list_returns_last_page(self):
        response = self.client.get(
            '/api/products/',
            {'limit': 40, 'offset': 40},
            HTTP_HOST='localhost',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
        self.assertIsNone(response.data['next_offset'])
        self.assertFalse(response.data['has_next'])

    def test_category_list_includes_ai_label(self):
        response = self.client.get('/api/products/categories/', HTTP_HOST='localhost')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['ai_label'], 'vacuum')
