from django.urls import path
from .views import VideoPresignedUrlView, VideoUploadCompleteView, VideoView, ReviewListCreateView, ReviewDetailView

urlpatterns = [
    path('', VideoView.as_view(), name='video-list-create'),
    path('presigned-url/', VideoPresignedUrlView.as_view(), name='video-presigned-url'),
    path('<int:video_upload_id>/complete/', VideoUploadCompleteView.as_view(), name='video-upload-complete'),
    path('<int:video_id>/reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('<int:video_id>/reviews/<int:review_id>/', ReviewDetailView.as_view(), name='review-detail'),
]
