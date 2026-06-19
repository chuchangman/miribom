from rest_framework import serializers
from .models import Category, Product, Bookmark


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'ai_label', 'display_order']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(source='category_id', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'product_id', 'title', 'brand', 'image', 'lprice', 'link', 'category', 'price_updated_at']


class BookmarkSerializer(serializers.ModelSerializer):
    product = ProductSerializer(source='product_id', read_only=True)

    class Meta:
        model = Bookmark
        fields = ['id', 'product', 'created_at']


class BookmarkCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(help_text='북마크할 제품의 ID')
