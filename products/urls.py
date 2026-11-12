from django.urls import path
from .views import (
    CategoryListView, ProductListView, ProductDetailView,
    SellerProductListCreateView, SellerProductDetailView,
    ProductVideoCreateView, ProductImageCreateView,
)

urlpatterns = [
    # public
    path("categories/", CategoryListView.as_view()),
    path("products/", ProductListView.as_view()),
    path("products/<int:pk>/", ProductDetailView.as_view()),

    # seller
    path("seller/products/", SellerProductListCreateView.as_view()),
    path("seller/products/<int:pk>/", SellerProductDetailView.as_view()),
    path("seller/products/<int:pk>/videos/", ProductVideoCreateView.as_view()),
    path("seller/products/<int:pk>/images/", ProductImageCreateView.as_view()),
]