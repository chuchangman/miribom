from django.db import models
from users.models import User

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=50, null=False)
    slug = models.CharField(max_length=100, null=False)
    ai_label = models.CharField(max_length=100, null=False)
    display_order = models.IntegerField()

class Product(models.Model):
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_id = models.CharField(max_length=180, null=False)
    title = models.CharField(max_length=255, null=False)
    brand = models.CharField(max_length=180, null=True, blank=True)
    image = models.CharField(max_length=500)
    lprice = models.IntegerField(null=True, blank=True)
    link = models.CharField(max_length=500)
    price_updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Bookmark(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)