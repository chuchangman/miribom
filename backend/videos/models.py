from django.db import models
from users.models import User
from products.models import Product

# Create your models here.
class VideoUpload(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    video_url = models.CharField(max_length=500, null=False)
    thumbnail_url = models.CharField(max_length=500)
    r2_key = models.CharField(max_length=500, blank=True, default='')
    predicted_category_id = models.ForeignKey('products.Category', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Video(models.Model):
    video_upload_id = models.OneToOneField(VideoUpload, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    user_id = models.ForeignKey('users.User', on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    video_id = models.ForeignKey(Video, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(null=False)
    content = models.TextField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['video_id', 'user_id'], name='unique_review_per_user_video')
        ]

class Like(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    video_id = models.ForeignKey(Video, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, null=False)

class Comment(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    video_id = models.ForeignKey(Video, on_delete=models.CASCADE, null=False)
    content = models.TextField(null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True)

class Report(models.Model):
    reporter_id = models.ForeignKey(User, on_delete=models.CASCADE)
    video_id = models.ForeignKey(Video, on_delete=models.CASCADE)
    comment_id = models.ForeignKey(Comment, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.CharField(max_length=30, null=False)
    description = models.TextField()
    status = models.CharField(max_length=30, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)