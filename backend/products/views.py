from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Category, Product, Bookmark
from .serializers import CategorySerializer, ProductSerializer, BookmarkSerializer, BookmarkCreateSerializer


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
        ],
        responses=ProductSerializer(many=True),
    )
    def get(self, request):
        queryset = Product.objects.select_related('category_id').all()

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

        queryset = queryset.order_by('lprice')
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses=ProductSerializer, summary='제품 상세 조회')
    def get(self, request, pk):
        try:
            product = Product.objects.select_related('category_id').get(pk=pk)
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
