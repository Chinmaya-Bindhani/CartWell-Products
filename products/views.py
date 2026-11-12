from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from django.db.models import Q, Avg
from rest_framework import filters
from .models import Category, Product
from .serializer import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    SellerProductSerializer, ProductVideoSerializer, ProductImageSerializer,
)


class SellerProductListCreateView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]   # TODO: IsSeller later
    serializer_class = SellerProductSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = Product.objects.all()
        seller_id = self.request.query_params.get("seller_id")   # TODO: from token later
        if seller_id:
            qs = qs.filter(seller_id=seller_id)
        return qs

    def get_serializer(self, *args, **kwargs): # used for bunch seeeding
        if isinstance(kwargs.get("data"), list):
            kwargs["many"] = True
        return super().get_serializer(*args, **kwargs)

class SellerProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]   # TODO: IsSeller + IsProductOwner later
    serializer_class = SellerProductSerializer
    queryset = Product.objects.all()

class ProductVideoCreateView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductVideoSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        serializer.save(product=get_object_or_404(Product, pk=self.kwargs["pk"]))


class ProductImageCreateView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductImageSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def perform_create(self, serializer):
        serializer.save(product=get_object_or_404(Product, pk=self.kwargs["pk"]))

class CategoryListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(parent__isnull=True).prefetch_related("children")


class ProductListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "brand", "description", "category__name"]

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True).select_related("category")

        slug = self.request.query_params.get("category")
        if slug:
            qs = qs.filter(Q(category__slug=slug) | Q(category__parent__slug=slug))

        brand = self.request.query_params.get("brand")
        if brand:
            qs = qs.filter(brand__iexact=brand)

        return qs


class ProductDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductDetailSerializer

    def get_queryset(self):
        return (
            Product.objects.filter(is_active=True)
            .select_related("category")
            .prefetch_related("images", "videos")
            .annotate(avg_rating=Avg("reviews__rating"))
        )