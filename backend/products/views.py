import json
import hashlib
from openai import OpenAI
from django.conf import settings
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Avg, Count, Q, F
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Category, Product, Bookmark
from .serializers import CategorySerializer, ProductSerializer, BookmarkSerializer, BookmarkCreateSerializer, RecommendationRequestSerializer
from .recommendation_questions import CATEGORY_QUESTIONS


def _product_qs_with_stats():
    return Product.objects.select_related('category_id').annotate(
        avg_rating=Avg(
            'video__review__rating',
            filter=Q(video__is_deleted=False) & Q(video__review__is_deleted=False),
        ),
        review_count=Count(
            'video__review',
            filter=Q(video__is_deleted=False) & Q(video__review__is_deleted=False),
            distinct=True,
        ),
    )


class CategoryListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses=CategorySerializer(many=True), summary='카테고리 목록')
    def get(self, request):
        categories = Category.objects.all().order_by('display_order')
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class ProductListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='제품 목록 및 검색',
        parameters=[
            OpenApiParameter(name='q', description='제목 또는 브랜드 키워드 검색', required=False, type=str),
            OpenApiParameter(name='category', description='카테고리 ID 필터', required=False, type=int),
            OpenApiParameter(name='limit', description='조회할 제품 수 (최대 40)', required=False, type=int),
            OpenApiParameter(name='offset', description='조회 시작 위치', required=False, type=int),
        ],
    )
    def get(self, request):
        queryset = _product_qs_with_stats().filter(
            title__gt='', image__gt='', lprice__isnull=False, lprice__gt=0
        )

        category_id = request.query_params.get('category')
        if category_id:
            try:
                category_id = int(category_id)
            except ValueError:
                return Response({'detail': 'category는 정수여야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)
            queryset = queryset.filter(category_id=category_id)

        q = request.query_params.get('q')
        if q:
            queryset = queryset.filter(Q(title__icontains=q) | Q(brand__icontains=q))

        try:
            limit = int(request.query_params.get('limit', 40))
            offset = int(request.query_params.get('offset', 0))
        except ValueError:
            return Response(
                {'detail': 'limit과 offset은 정수여야 합니다.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not (1 <= limit <= 40) or offset < 0:
            return Response(
                {'detail': 'limit은 1~40, offset은 0 이상이어야 합니다.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = queryset.order_by('lprice', 'id')
        page = list(queryset[offset:offset + limit + 1])
        has_next = len(page) > limit
        products = page[:limit]
        serializer = ProductSerializer(products, many=True)

        return Response({
            'results': serializer.data,
            'next_offset': offset + limit if has_next else None,
            'has_next': has_next,
        })


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses=ProductSerializer, summary='제품 상세 조회')
    def get(self, request, pk):
        try:
            product = _product_qs_with_stats().get(pk=pk)
        except Product.DoesNotExist:
            return Response({'detail': '상품을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProductSerializer(product)
        return Response(serializer.data)


class BookmarkListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=BookmarkSerializer(many=True), summary='북마크 목록 조회')
    def get(self, request):
        bookmarks = Bookmark.objects.filter(user_id=request.user).select_related('product_id__category_id')
        serializer = BookmarkSerializer(bookmarks, many=True)
        return Response(serializer.data)

    @extend_schema(request=BookmarkCreateSerializer, responses=BookmarkSerializer, summary='북마크 추가')
    def post(self, request):
        serializer = BookmarkCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(pk=serializer.validated_data['product_id'])
        except Product.DoesNotExist:
            return Response({'detail': '상품을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        bookmark, created = Bookmark.objects.get_or_create(user_id=request.user, product_id=product)
        if not created:
            return Response({'detail': '이미 북마크된 상품입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BookmarkSerializer(bookmark)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BookmarkDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(responses=None, summary='북마크 삭제')
    def delete(self, request, pk):
        try:
            bookmark = Bookmark.objects.get(pk=pk, user_id=request.user)
        except Bookmark.DoesNotExist:
            return Response({'detail': '북마크를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
        bookmark.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BookmarkToggleView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='제품 즐겨찾기 토글 (추가/취소)',
        responses={
            200: {'type': 'object', 'properties': {'bookmarked': {'type': 'boolean'}}},
            404: {'description': '제품 없음'},
        },
    )
    def post(self, request, product_id):
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({'detail': '상품을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        bookmark = Bookmark.objects.filter(user_id=request.user, product_id=product).first()
        if bookmark:
            bookmark.delete()
            bookmarked = False
        else:
            Bookmark.objects.create(user_id=request.user, product_id=product)
            bookmarked = True

        return Response(
            {'bookmarked': bookmarked},
            status=status.HTTP_201_CREATED if bookmarked else status.HTTP_200_OK,
        )


class RecommendationQuestionsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='선택한 카테고리의 세부 질문 목록 조회',
        parameters=[
            OpenApiParameter(name='category_ids', type=str, location=OpenApiParameter.QUERY, required=True, description='카테고리 id 목록 (쉼표 구분, 예: 1,2,4)'),
        ],
        responses={200: {'type': 'object'}},
    )
    def get(self, request):
        raw = request.query_params.get('category_ids', '')
        try:
            category_ids = [int(i) for i in raw.split(',') if i.strip()]
        except ValueError:
            return Response({'detail': 'category_ids는 정수 목록이어야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)

        if not category_ids:
            return Response({'detail': 'category_ids를 입력해주세요.'}, status=status.HTTP_400_BAD_REQUEST)

        categories = Category.objects.filter(id__in=category_ids).order_by('display_order')
        result = []
        for cat in categories:
            questions = CATEGORY_QUESTIONS.get(cat.id, [])
            if questions:
                result.append({
                    'category_id': cat.id,
                    'category_name': cat.name,
                    'questions': questions,
                })

        return Response({'categories': result})


def _get_product_filter_from_answers(cat_id, answers):
    """설문 답변을 바탕으로 제품 키워드 필터(Q)와 최소가격을 반환합니다."""
    q = Q()
    min_price = None

    if cat_id == 1:  # 세탁·건조
        product_type = answers.get('product_type')
        if product_type == 'combo':
            q &= Q(title__icontains='세탁건조') | Q(title__icontains='워시콤보') | Q(title__icontains='일체형')
        elif product_type == 'dryer':
            q &= Q(title__icontains='건조기')
            q &= ~(Q(title__icontains='세탁건조일체형') | Q(title__icontains='워시콤보'))
            if answers.get('dryer_type') == 'heat_pump':
                q &= Q(title__icontains='히트펌프')
        elif product_type == 'washer':
            q &= Q(title__icontains='세탁기')
            q &= ~Q(title__icontains='건조기')
            washer_type = answers.get('washer_type')
            if washer_type == 'drum':
                q &= Q(title__icontains='드럼')
            elif washer_type == 'agitator':
                q &= Q(title__icontains='통돌이')

    elif cat_id == 2:  # 냉장고
        fridge_type = answers.get('fridge_type')
        if fridge_type == 'mini':
            q &= Q(title__icontains='미니') | Q(title__icontains='소형') | Q(title__icontains='1도어')
        elif fridge_type == 'side_by_side':
            q &= Q(title__icontains='양문')
        elif fridge_type == 'french_door':
            q &= Q(title__icontains='프렌치')
        elif fridge_type == 'standard':
            # 일반형 냉장고: 소형/미니 제목 키워드 제외 + 3인 이상이면 최소가격 기준 적용
            q &= ~(Q(title__icontains='미니') | Q(title__icontains='1도어'))
            family_size = answers.get('family_size', '')
            if family_size in ('3_4', '5+'):
                min_price = 300_000  # 가족용 일반 냉장고 기준가

    elif cat_id == 4:  # 청소기
        vacuum_type = answers.get('vacuum_type')
        if vacuum_type == 'wireless':
            # 무선 청소기: 핸디/소형 제외, 일정 가격 이상만
            q &= Q(title__icontains='무선')
            q &= ~(Q(title__icontains='핸디청소기') | Q(title__icontains='미니청소기') | Q(title__icontains='소형청소기'))
            min_price = 100_000
        elif vacuum_type == 'robot':
            q &= Q(title__icontains='로봇청소기')
        elif vacuum_type == 'wired':
            q &= Q(title__icontains='유선청소기') | Q(title__icontains='유선 청소기')
        elif vacuum_type == 'handy':
            q &= Q(title__icontains='핸디') | Q(title__icontains='미니청소기')

    elif cat_id == 5:  # 계절가전
        seasonal_type = answers.get('seasonal_type')
        if seasonal_type == 'aircon':
            install = answers.get('aircon_install')
            if install == 'wall':
                q &= Q(title__icontains='벽걸이') & Q(title__icontains='에어컨')
            elif install == 'stand':
                q &= Q(title__icontains='스탠드') & Q(title__icontains='에어컨')
            else:
                q &= Q(title__icontains='에어컨')
        elif seasonal_type == 'fan':
            fan_type = answers.get('fan_type')
            if fan_type == 'circulator':
                q &= Q(title__icontains='서큘레이터')
            else:
                q &= Q(title__icontains='선풍기') | Q(title__icontains='서큘레이터')
        elif seasonal_type == 'heater':
            q &= Q(title__icontains='온풍기') | Q(title__icontains='히터') | Q(title__icontains='라디에이터')

    elif cat_id == 6:  # 제습기·가습기
        humidifier_type = answers.get('humidifier_type')
        if humidifier_type == 'dehumidifier':
            q &= Q(title__icontains='제습기')
        elif humidifier_type == 'humidifier':
            q &= Q(title__icontains='가습기')
            method = answers.get('humidifier_method')
            if method == 'ultrasonic':
                q &= Q(title__icontains='초음파')
            elif method == 'heated':
                q &= Q(title__icontains='가열')
            elif method == 'complex':
                q &= Q(title__icontains='복합')
        elif humidifier_type == 'both':
            q &= Q(title__icontains='제습기') | Q(title__icontains='가습기')

    return q, min_price


BUDGET_MAX_MAP = {
    'under_30':   300_000,
    '30_to_100':  1_000_000,
    '100_to_300': 3_000_000,
    'over_300':   None,
}

BUDGET_LABEL_MAP = {
    'under_30':   '30만원 이하',
    '30_to_100':  '30~100만원',
    '100_to_300': '100~300만원',
    'over_300':   '300만원 이상',
}


class RecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='추천 설문 사전 데이터 (주거 형태·면적 자동 기입 + 카테고리 목록)',
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'housing_type': {'type': 'string'},
                    'area_size': {'type': 'integer', 'nullable': True},
                    'categories': {'type': 'array'},
                    'budget_options': {'type': 'array'},
                },
            },
        },
    )
    def get(self, request):
        user = request.user
        categories = Category.objects.all().order_by('display_order')
        return Response({
            'housing_type': user.housing_type or '',
            'area_size': user.area_size,
            'categories': CategorySerializer(categories, many=True).data,
            'budget_options': [
                {'value': k, 'label': v} for k, v in BUDGET_LABEL_MAP.items()
            ],
        })

    @extend_schema(
        summary='질문형 AI 제품 추천',
        request=RecommendationRequestSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'results': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'category': {'type': 'object'},
                                'reason': {'type': 'string'},
                                'products': {'type': 'array'},
                            },
                        },
                    },
                },
            },
            400: {'description': '유효하지 않은 요청'},
        },
    )
    def post(self, request):
        serializer = RecommendationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        housing_type = data['housing_type']
        area_size = data.get('area_size')
        category_ids = data['category_ids']
        budget = data['budget']
        category_answers = data.get('category_answers', {})
        max_price = BUDGET_MAX_MAP[budget]

        categories = list(
            Category.objects.filter(id__in=category_ids).order_by('display_order')
        )
        if not categories:
            return Response({'detail': '유효한 카테고리가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)

        raw_key = f'{housing_type}:{area_size}:{sorted(category_ids)}:{budget}:{sorted((k, sorted(v.items())) for k, v in category_answers.items())}'
        cache_key = 'rec:' + hashlib.md5(raw_key.encode()).hexdigest()
        ai_result = cache.get(cache_key)
        if ai_result is None:
            ai_result = self._call_gms(housing_type, area_size, budget, categories, category_answers)
            cache.set(cache_key, ai_result, timeout=3600)

        cat_map = {c.id: c for c in categories}
        results = []
        for item in ai_result:
            cat_id = item.get('category_id')
            reason = item.get('reason', '')
            cat = cat_map.get(cat_id)
            if not cat:
                continue

            qs = _product_qs_with_stats().filter(
                category_id=cat_id,
                title__gt='', image__gt='', lprice__isnull=False, lprice__gt=0,
            )
            if max_price:
                qs = qs.filter(lprice__lte=max_price)

            extra_filter, min_price_override = _get_product_filter_from_answers(
                cat_id, category_answers.get(str(cat_id), {})
            )
            if extra_filter:
                qs = qs.filter(extra_filter)
            if min_price_override:
                qs = qs.filter(lprice__gte=min_price_override)

            products = list(
                qs.order_by(F('avg_rating').desc(nulls_last=True), 'lprice')[:5]
            )
            if not products:
                continue

            results.append({
                'category': CategorySerializer(cat).data,
                'reason': reason,
                'products': ProductSerializer(products, many=True).data,
            })

        return Response({'results': results})

    def _build_answers_desc(self, category_answers, categories):
        if not category_answers:
            return ''
        lines = []
        for cat in categories:
            answers = category_answers.get(str(cat.id), {})
            if answers:
                answer_str = ', '.join(f'{k}: {v}' for k, v in answers.items())
                lines.append(f'  [{cat.name}] {answer_str}')
        return '\n'.join(lines)

    def _call_gms(self, housing_type, area_size, budget, categories, category_answers=None):
        area_desc = f'{area_size}평' if area_size else '면적 정보 없음'
        budget_label = BUDGET_LABEL_MAP[budget]
        category_info = '\n'.join(
            f'- id:{c.id} | {c.name} | {c.ai_label}' for c in categories
        )
        cat_ids = [c.id for c in categories]
        answers_desc = self._build_answers_desc(category_answers, categories)
        answers_section = f'\n세부 요구사항:\n{answers_desc}' if answers_desc else ''

        prompt = f"""사용자 정보:
- 주거 형태: {housing_type}
- 면적: {area_desc}
- 예산: {budget_label}{answers_section}

카테고리 상세:
{category_info}

위 조건과 세부 요구사항을 반영해 카테고리를 추천 우선순위 순으로 정렬하고,
각각 추천 이유를 한 문장으로 작성해 아래 JSON 형식으로만 응답하세요.
모든 id({cat_ids})를 반드시 포함하세요.

{{
  "recommendations": [
    {{"category_id": 1, "reason": "이유"}},
    ...
  ]
}}"""

        try:
            client = OpenAI(
                api_key=settings.GMS_API_KEY,
                base_url=settings.GMS_BASE_URL,
            )
            response = client.chat.completions.create(
                model=settings.GMS_MODEL,
                messages=[
                    {'role': 'developer', 'content': '가전제품 추천 전문가입니다. JSON 형식으로만 응답하세요.'},
                    {'role': 'user', 'content': prompt},
                ],
                max_completion_tokens=512,
            )
            content = response.choices[0].message.content.strip()
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            return json.loads(content)['recommendations']
        except Exception:
            return [{'category_id': c.id, 'reason': ''} for c in categories]
