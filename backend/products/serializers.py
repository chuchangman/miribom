from rest_framework import serializers
from django.db.models import Avg, Count
from .models import Category, Product, Bookmark


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'ai_label', 'display_order']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(source='category_id', read_only=True)
    avg_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'product_id', 'title', 'brand', 'image', 'lprice', 'link', 'category', 'price_updated_at', 'avg_rating', 'review_count']

    def get_avg_rating(self, obj):
        if 'avg_rating' in obj.__dict__:
            val = obj.__dict__['avg_rating']
            return round(val, 1) if val is not None else None
        from videos.models import Review
        result = Review.objects.filter(
            video_id__product_id=obj,
            video_id__is_deleted=False,
            is_deleted=False,
        ).aggregate(avg=Avg('rating'))
        val = result['avg']
        return round(val, 1) if val is not None else None

    def get_review_count(self, obj):
        if 'review_count' in obj.__dict__:
            return obj.__dict__['review_count']
        from videos.models import Review
        return Review.objects.filter(
            video_id__product_id=obj,
            video_id__is_deleted=False,
            is_deleted=False,
        ).count()


class BookmarkSerializer(serializers.ModelSerializer):
    product = ProductSerializer(source='product_id', read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'product', 'created_at']


class BookmarkCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(help_text='북마크할 제품의 ID')


BUDGET_CHOICES = ['under_30', '30_to_100', '100_to_300', 'over_300']

class RecommendationRequestSerializer(serializers.Serializer):
    housing_type = serializers.CharField(max_length=20)
    area_size = serializers.IntegerField(min_value=1, allow_null=True, required=False)
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text='관심 카테고리 id 목록 (1개 이상)',
    )
    budget = serializers.ChoiceField(
        choices=BUDGET_CHOICES,
        help_text='under_30 / 30_to_100 / 100_to_300 / over_300',
    )
    category_answers = serializers.DictField(
        child=serializers.DictField(child=serializers.JSONField()),
        required=False,
        default=dict,
        help_text='카테고리별 세부 질문 답변 {"category_id": {"question_id": "answer"}}',
    )
