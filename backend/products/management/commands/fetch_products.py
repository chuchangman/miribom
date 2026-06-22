import time
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from products.models import Category, Product


NAVER_SHOP_URL = 'https://openapi.naver.com/v1/search/shop.json'

# 카테고리 slug별 세부 검색어 목록
# 구체적인 키워드로 관련 없는 상품 유입 최소화
CATEGORY_QUERIES = {
    'washer-dryer': [
        '드럼세탁기',
        '통돌이세탁기',
        '히트펌프건조기',
        '세탁건조일체형',
    ],
    'refrigerator': [
        '일반냉장고',
        '양문형냉장고',
        '프렌치도어냉장고',
        '미니냉장고 소형',
    ],
    'kitchen-appliance': [
        '가정용전자레인지',
        '에어프라이어',
        '전기밥솥',
        '캡슐커피머신',
        '블렌더믹서기',
    ],
    'vacuum': [
        '무선스틱청소기',
        '로봇청소기',
        '유선청소기',
        '핸디청소기 소형',
    ],
    'seasonal': [
        '벽걸이에어컨',
        '스탠드에어컨',
        '서큘레이터선풍기',
        '전기온풍기히터',
    ],
    'dehumidifier-humidifier': [
        '가정용제습기',
        '초음파가습기',
        '가열식가습기',
        '복합식가습기',
    ],
    'pc-peripheral': [
        '27인치모니터',
        '기계식키보드',
        '무선마우스',
        '게이밍헤드셋',
        '화상회의웹캠',
    ],
    'projector': [
        '가정용빔프로젝터',
        '미니빔프로젝터',
        '4K빔프로젝터',
    ],
}


class Command(BaseCommand):
    help = '네이버 쇼핑 API로 카테고리별 세부 검색어 기반 가전제품 수집'

    def add_arguments(self, parser):
        parser.add_argument('--display', type=int, default=100, help='검색어당 수집할 상품 수 (최대 100)')

    def handle(self, *args, **options):
        display = options['display']
        if not (1 <= display <= 100):
            raise SystemExit('오류: --display는 1~100 사이의 값이어야 합니다.')

        headers = {
            'X-Naver-Client-Id': settings.NAVER_CLIENT_ID,
            'X-Naver-Client-Secret': settings.NAVER_CLIENT_SECRET,
        }

        categories = Category.objects.filter(slug__in=CATEGORY_QUERIES.keys()).order_by('display_order')
        if not categories.exists():
            self.stdout.write(self.style.WARNING('수집 대상 카테고리가 없습니다. 카테고리 fixtures를 먼저 로드하세요.'))
            return

        total_created = 0
        total_existing = 0
        total_skipped = 0

        for category in categories:
            queries = CATEGORY_QUERIES.get(category.slug, [])
            self.stdout.write(f'\n[{category.name}] 검색어 {len(queries)}개로 수집 시작...')

            cat_created = 0
            cat_existing = 0
            cat_skipped = 0

            for query in queries:
                self.stdout.write(f'  검색어: "{query}"')

                try:
                    response = requests.get(
                        NAVER_SHOP_URL,
                        headers=headers,
                        params={'query': query, 'display': display, 'sort': 'sim'},
                        timeout=10,
                    )
                    response.raise_for_status()
                except requests.RequestException as e:
                    self.stdout.write(self.style.ERROR(f'    API 오류: {e}'))
                    continue

                items = response.json().get('items', [])
                q_created = 0
                q_skipped = 0

                for item in items:
                    product_id = item.get('productId', '')
                    if not product_id:
                        continue

                    title = item.get('title', '').replace('<b>', '').replace('</b>', '').strip()
                    image = item.get('image', '').strip()
                    lprice_raw = item.get('lprice', '0')
                    lprice = int(lprice_raw) if lprice_raw else None

                    if not title or not image or not lprice:
                        q_skipped += 1
                        continue

                    _, created = Product.objects.update_or_create(
                        product_id=product_id,
                        defaults={
                            'category_id': category,
                            'title': title,
                            'brand': item.get('brand', ''),
                            'image': image,
                            'lprice': lprice,
                            'link': item.get('link', ''),
                        },
                    )
                    if created:
                        q_created += 1
                    else:
                        cat_existing += 1

                cat_created += q_created
                cat_skipped += q_skipped
                self.stdout.write(f'    → 신규 {q_created}개, 스킵 {q_skipped}개')

                # API 호출 간격 (과도한 요청 방지)
                time.sleep(0.3)

            self.stdout.write(self.style.SUCCESS(
                f'  [{category.name}] 합계 - 신규: {cat_created}개, 기존: {cat_existing}개, 스킵: {cat_skipped}개'
            ))
            total_created += cat_created
            total_existing += cat_existing
            total_skipped += cat_skipped

        self.stdout.write(self.style.SUCCESS(
            f'\n전체 완료 - 신규: {total_created}개, 기존: {total_existing}개, 스킵: {total_skipped}개'
        ))
