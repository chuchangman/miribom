from django.db import models

# Create your models here.
class User(models.Model):
    nickname = models.CharField(max_length=50, null=False)
    profile_image_url = models.CharField(max_length=512)
    housing_type = models.CharField(max_length=20)
    area_size = models.IntegerField(null=True, blank=True)
    living_updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)

class Social_User(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    oauth_provider = models.CharField(max_length=20, null=False)
    oauth_id = models.CharField(max_length=255, null=False)
    email = models.CharField(max_length=255)

class Email_User(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    email = models.CharField(max_length=255, null=False)
    password = models.CharField(max_length=255, null=False)