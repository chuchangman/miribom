from django.urls import path
from .views import (
    VideoPresignedUrlView, VideoUploadCompleteView, VideoView,
    CommentListCreateView, CommentDetailView,
    ReviewListCreateView, ReviewDetailView,
    LikeToggleView, LikedVideoListView,
    MyVideoListView, MyReviewListView,
)

urlpatterns = [
    path('', VideoView.as_view(), name='video-list-create'),
    path('liked/', LikedVideoListView.as_view(), name='liked-video-list'),
    path('my/', MyVideoListView.as_view(), name='my-video-list'),
    path('my-reviews/', MyReviewListView.as_view(), name='my-review-list'),
    path('presigned-url/', VideoPresignedUrlView.as_view(), name='video-presigned-url'),
    path('<int:video_upload_id>/complete/', VideoUploadCompleteView.as_view(), name='video-upload-complete'),
    path('<int:video_id>/like/', LikeToggleView.as_view(), name='video-like-toggle'),
    path('<int:video_id>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('<int:video_id>/comments/<int:comment_id>/', CommentDetailView.as_view(), name='comment-detail'),
    path('<int:video_id>/reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('<int:video_id>/reviews/<int:review_id>/', ReviewDetailView.as_view(), name='review-detail'),
]
