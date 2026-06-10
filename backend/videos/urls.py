from django.urls import path
from .views import VideoPresignedUrlView, VideoUploadCompleteView, VideoView

urlpatterns = [
    path('', VideoView.as_view(), name='video-list-create'),
    path('presigned-url/', VideoPresignedUrlView.as_view(), name='video-presigned-url'),
    path('<int:video_upload_id>/complete/', VideoUploadCompleteView.as_view(), name='video-upload-complete'),
]
