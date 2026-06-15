import uuid
import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from django.conf import settings
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from products.models import Product
from .models import VideoUpload, Video, Review
from .serializers import (
    VideoPresignedUrlSerializer,
    VideoUploadCompleteSerializer,
    VideoCreateSerializer,
    VideoFeedSerializer,
    ReviewCreateSerializer,
    ReviewDetailSerializer,
)


def get_r2_client():
    return boto3.client(
        's3',
        endpoint_url=settings.R2_ENDPOINT_URL,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        config=Config(signature_version='s3v4'),
        region_name='auto',
    )


class VideoPresignedUrlView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='영상 업로드용 Presigned URL 발급',
        request=VideoPresignedUrlSerializer,
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'video_upload_id': {'type': 'integer'},
                    'presigned_url': {'type': 'string'},
                    'r2_key': {'type': 'string'},
                },
            },
            400: {'description': '파일 형식 또는 크기 오류'},
        },
    )
    def post(self, request):
        serializer = VideoPresignedUrlSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        filename = data['filename']
        content_type = data['content_type']
        file_size = data['file_size']

        if file_size > settings.VIDEO_MAX_SIZE_BYTES:
            max_mb = settings.VIDEO_MAX_SIZE_BYTES // (1024 * 1024)
            return Response(
                {'detail': f'파일 크기는 {max_mb}MB를 초과할 수 없습니다.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ext = filename.rsplit('.', 1)[-1] if '.' in filename else 'mp4'
        r2_key = f"videos/{request.user.id}/{uuid.uuid4()}.{ext}"

        try:
            client = get_r2_client()
            presigned_url = client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': settings.R2_BUCKET_NAME,
                    'Key': r2_key,
                    'ContentType': content_type,
                },
                ExpiresIn=600,
            )
        except (BotoCoreError, ClientError, ValueError):
            return Response(
                {'detail': 'R2 서비스에 연결할 수 없습니다. 환경 설정을 확인해주세요.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        video_upload = VideoUpload.objects.create(
            user_id=request.user,
            video_url='',
            thumbnail_url='',
            r2_key=r2_key,
            status='pending',
        )

        return Response(
            {
                'video_upload_id': video_upload.id,
                'presigned_url': presigned_url,
                'r2_key': r2_key,
            },
            status=status.HTTP_201_CREATED,
        )


class VideoUploadCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='영상 업로드 완료 상태 저장',
        request=VideoUploadCompleteSerializer,
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'video_upload_id': {'type': 'integer'},
                    'video_url': {'type': 'string'},
                    'status': {'type': 'string'},
                },
            },
            400: {'description': 'r2_key 누락 또는 이미 완료된 업로드'},
            403: {'description': '권한 없음'},
            404: {'description': '업로드 레코드 없음'},
        },
    )
    def patch(self, request, video_upload_id):
        serializer = VideoUploadCompleteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        r2_key = serializer.validated_data['r2_key']

        try:
            video_upload = VideoUpload.objects.get(id=video_upload_id)
        except VideoUpload.DoesNotExist:
            return Response({'detail': '업로드 레코드를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        if video_upload.user_id != request.user:
            return Response({'detail': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

        if video_upload.status == 'uploaded':
            return Response({'detail': '이미 완료된 업로드입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        if video_upload.r2_key != r2_key:
            return Response({'detail': '유효하지 않은 r2_key입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        video_url = f"{settings.R2_PUBLIC_URL}/{r2_key}"
        video_upload.video_url = video_url
        video_upload.status = 'uploaded'
        video_upload.save(update_fields=['video_url', 'status'])

        return Response(
            {
                'video_upload_id': video_upload.id,
                'video_url': video_url,
                'status': video_upload.status,
            },
            status=status.HTTP_200_OK,
        )


class VideoView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return super().get_permissions()

    @extend_schema(
        summary='영상 피드 조회 (전체 또는 특정 제품)',
        parameters=[
            OpenApiParameter(name='product_id', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description='특정 제품의 영상만 조회'),
            OpenApiParameter(name='cursor', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description='마지막으로 받은 video id (다음 페이지 조회용)'),
        ],
        responses={200: VideoFeedSerializer(many=True)},
    )
    def get(self, request):
        product_id = request.query_params.get('product_id')
        cursor = request.query_params.get('cursor')

        if product_id is not None:
            try:
                product_id = int(product_id)
            except ValueError:
                return Response({'detail': 'product_id는 정수여야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)

        if cursor is not None:
            try:
                cursor = int(cursor)
            except ValueError:
                return Response({'detail': 'cursor는 정수여야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)

        qs = Video.objects.filter(is_deleted=False).select_related(
            'video_upload_id', 'user_id', 'product_id'
        ).order_by('-id')

        if product_id:
            qs = qs.filter(product_id=product_id)

        if cursor:
            qs = qs.filter(id__lt=cursor)

        videos = qs[:20]
        serializer = VideoFeedSerializer(videos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary='영상 등록 (VideoUpload → Video, 제품 연결)',
        request=VideoCreateSerializer,
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'video_url': {'type': 'string'},
                    'product_id': {'type': 'integer'},
                },
            },
            400: {'description': '유효하지 않은 요청'},
            403: {'description': '권한 없음'},
            404: {'description': 'VideoUpload 또는 Product 없음'},
        },
    )
    def post(self, request):
        serializer = VideoCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            video_upload = VideoUpload.objects.get(id=data['video_upload_id'])
        except VideoUpload.DoesNotExist:
            return Response({'detail': 'VideoUpload를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        if video_upload.user_id != request.user:
            return Response({'detail': '권한이 없습니다.'}, status=status.HTTP_403_FORBIDDEN)

        if video_upload.status != 'uploaded':
            return Response({'detail': '업로드가 완료되지 않은 영상입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        if Video.objects.filter(video_upload_id=video_upload).exists():
            return Response({'detail': '이미 등록된 영상입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=data['product_id'])
        except Product.DoesNotExist:
            return Response({'detail': '제품을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        video = Video.objects.create(
            video_upload_id=video_upload,
            product_id=product,
            user_id=request.user,
        )

        return Response(
            {
                'id': video.id,
                'video_url': video_upload.video_url,
                'product_id': product.id,
            },
            status=status.HTTP_201_CREATED,
        )


class ReviewListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return super().get_permissions()

    @extend_schema(
        summary='영상 리뷰 목록 조회',
        parameters=[
            OpenApiParameter(name='cursor', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False, description='마지막으로 받은 review id (다음 페이지 조회용)'),
        ],
        responses={
            200: ReviewDetailSerializer(many=True),
            404: {'description': '영상 없음'},
        },
    )
    def get(self, request, video_id):
        try:
            video = Video.objects.get(id=video_id, is_deleted=False)
        except Video.DoesNotExist:
            return Response({'detail': '영상을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        cursor = request.query_params.get('cursor')
        if cursor is not None:
            try:
                cursor = int(cursor)
            except ValueError:
                return Response({'detail': 'cursor는 정수여야 합니다.'}, status=status.HTTP_400_BAD_REQUEST)

        qs = Review.objects.filter(
            video_id=video, is_deleted=False
        ).select_related(
            'user_id', 'video_id__product_id'
        ).order_by('-id')

        if cursor:
            qs = qs.filter(id__lt=cursor)

        reviews = qs[:20]
        serializer = ReviewDetailSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary='리뷰 생성',
        request=ReviewCreateSerializer,
        responses={
            201: ReviewDetailSerializer,
            400: {'description': '유효하지 않은 요청 또는 이미 작성한 리뷰'},
            403: {'description': '본인 영상이 아님'},
            404: {'description': '영상 없음'},
        },
    )
    def post(self, request, video_id):
        try:
            video = Video.objects.select_related('product_id').get(id=video_id, is_deleted=False)
        except Video.DoesNotExist:
            return Response({'detail': '영상을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        if video.user_id != request.user:
            return Response({'detail': '본인이 업로드한 영상에만 리뷰를 작성할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = ReviewCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            review = Review.objects.create(
                video_id=video,
                user_id=request.user,
                rating=serializer.validated_data['rating'],
                content=serializer.validated_data['content'],
            )
        except IntegrityError:
            return Response({'detail': '이미 리뷰를 작성한 영상입니다.'}, status=status.HTTP_400_BAD_REQUEST)

        review.user_id = request.user
        review.video_id = video
        response_serializer = ReviewDetailSerializer(review)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ReviewDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='리뷰 상세 조회',
        responses={
            200: ReviewDetailSerializer,
            404: {'description': '리뷰 또는 영상 없음'},
        },
    )
    def get(self, request, video_id, review_id):
        try:
            Video.objects.get(id=video_id, is_deleted=False)
        except Video.DoesNotExist:
            return Response({'detail': '영상을 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            review = Review.objects.select_related(
                'user_id', 'video_id__product_id'
            ).get(id=review_id, video_id=video_id, is_deleted=False)
        except Review.DoesNotExist:
            return Response({'detail': '리뷰를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReviewDetailSerializer(review)
        return Response(serializer.data, status=status.HTTP_200_OK)
