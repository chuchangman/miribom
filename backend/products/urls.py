from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('', views.ProductListView.as_view(), name='product-list'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('<int:product_id>/bookmark/', views.BookmarkToggleView.as_view(), name='product-bookmark-toggle'),
    path('bookmarks/', views.BookmarkListView.as_view(), name='bookmark-list'),
    path('bookmarks/<int:pk>/', views.BookmarkDetailView.as_view(), name='bookmark-detail'),
]
