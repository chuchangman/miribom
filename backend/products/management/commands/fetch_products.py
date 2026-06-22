import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from products.models import Category, Product


NAVER_SHOP_URL = 'https://openapi.naver.com/v1/search/shop.json'

TARGET_SLUGS = [
    'washer-dryer',
    'refrigerator',
    'kitchen-appliance',
    'vacuum',
    'seasonal',
    'dehumidifier-humidifier',
    'pc-peripheral',
    'projector',
]


class Command(BaseCommand):
    help = '네이버 쇼핑 API로 카테고리별 가전제품 수집'

    def add_arguments(self, parser):
        parser.add_argument('--display', type=int, default=100, help='카테고리당 수집할 상품 수 (최대 100)')

    def handle(self, *args, **options):
        display = options['display']
        if not (1 <= display <= 100):
            raise SystemExit('오류: --display는 1~100 사이의 값이어야 합니다.')
        headers = {
            'X-Naver-Client-Id': settings.NAVER_CLIENT_ID,
            'X-Naver-Client-Secret': settings.NAVER_CLIENT_SECRET,
        }

        categories = Category.objects.filter(slug__in=TARGET_SLUGS).order_by('display_order')
        if not categories.exists():
            self.stdout.write(self.style.WARNING('수집 대상 카테고리가 없습니다. 카테고리 fixtures를 먼저 로드하세요.'))
            return

        for category in categories:
            self.stdout.write(f'[{category.name}] 수집 시작...')
            params = {
                'query': category.name,
                'display': display,
                'sort': 'sim',
            }

            try:
                response = requests.get(NAVER_SHOP_URL, headers=headers, params=params, timeout=10)
                response.raise_for_status()
            except requests.RequestException as e:
                self.stdout.write(self.style.ERROR(f'  API 오류: {e}'))
                continue

            items = response.json().get('items', [])
            created_count = 0
            existing_count = 0

            skipped_count = 0
            for item in items:
                product_id = item.get('productId', '')
                if not product_id:
                    continue

                title = item.get('title', '').replace('<b>', '').replace('</b>', '').strip()
                image = item.get('image', '').strip()
                lprice_raw = item.get('lprice', '0')
                lprice = int(lprice_raw) if lprice_raw else None

                if not title or not image or not lprice:
                    skipped_count += 1
                    continue

                _, created = Product.objects.update_or_create(
                    product_id=product_id,
                    defaults={
                        'title': title,
                        'brand': item.get('brand', ''),
                        'image': item.get('image', ''),
                        'lprice': lprice,
                        'link': item.get('link', ''),
                    },
                    create_defaults={'category_id': category},
                )
                if created:
                    created_count += 1
                else:
                    existing_count += 1

            self.stdout.write(self.style.SUCCESS(
                f'  완료 - 신규: {created_count}개, 기존: {existing_count}개, 불완전 스킵: {skipped_count}개'
            ))

        self.stdout.write(self.style.SUCCESS('모든 카테고리 수집 완료'))
