from rest_framework import serializers
from django.conf import settings
from .models import Video, VideoUpload, Review, Comment


class VideoPresignedUrlSerializer(serializers.Serializer):
    filename = serializers.CharField(max_length=255)
    content_type = serializers.ChoiceField(choices=[(t, t) for t in settings.VIDEO_ALLOWED_CONTENT_TYPES])
    file_size = serializers.IntegerField(min_value=1)


class VideoUploadCompleteSerializer(serializers.Serializer):
    r2_key = serializers.CharField(max_length=500)


class VideoCreateSerializer(serializers.Serializer):
    video_upload_id = serializers.IntegerField()
    product_id = serializers.IntegerField()


class CommentCreateSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=500)


class CommentUpdateSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=500)


class CommentDetailSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source='user_id.nickname')
    user_profile_image = serializers.CharField(source='user_id.profile_image_url')

    class Meta:
        model = Comment
        fields = [
            'id',
            'video_id',
            'user_id',
            'user_nickname',
            'user_profile_image',
            'content',
            'created_at',
            'updated_at',
        ]


class ReviewCreateSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)
    content = serializers.CharField(max_length=1000)


class ReviewDetailSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source='user_id.nickname')
    product_id = serializers.IntegerField(source='video_id.product_id.id')
    product_title = serializers.CharField(source='video_id.product_id.title')

    class Meta:
        model = Review
        fields = [
            'id',
            'video_id',
            'product_id',
            'product_title',
            'user_id',
            'user_nickname',
            'rating',
            'content',
            'created_at',
        ]


class VideoFeedSerializer(serializers.ModelSerializer):
    video_url = serializers.CharField(source='video_upload_id.video_url')
    thumbnail_url = serializers.CharField(source='video_upload_id.thumbnail_url')
    user_nickname = serializers.CharField(source='user_id.nickname')
    user_profile_image = serializers.CharField(source='user_id.profile_image_url')
    product_title = serializers.CharField(source='product_id.title')
    product_image = serializers.CharField(source='product_id.image')
    product_lprice = serializers.IntegerField(source='product_id.lprice')
    like_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Video
        fields = [
            'id',
            'video_url',
            'thumbnail_url',
            'user_id',
            'user_nickname',
            'user_profile_image',
            'product_id',
            'product_title',
            'product_image',
            'product_lprice',
            'like_count',
            'created_at',
        ]
