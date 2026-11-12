from django.db import transaction
from rest_framework import serializers
from .models import Category, Product, ProductImage, ProductVideo


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class CategorySerializer(serializers.ModelSerializer):
    children = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "children"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "is_primary"]


class ProductVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVideo
        fields = ["id", "video", "video_url", "title"]


class ProductListSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field="slug", read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "brand", "price", "category", "sku"]


class ProductDetailSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    videos = ProductVideoSerializer(many=True, read_only=True)
    avg_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "brand", "description", "price", "stock", "sku",
            "category", "images", "videos", "avg_rating", "created_at", "updated_at",
        ]


class SellerProductSerializer(serializers.ModelSerializer):
    images = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)
    videos = serializers.ListField(child=serializers.FileField(), write_only=True, required=False)
    video_urls = serializers.ListField(child=serializers.URLField(), write_only=True, required=False)

    class Meta:
        model = Product
        fields = [
            "id", "seller_id", "category", "name", "brand", "description",
            "price", "stock", "sku", "is_active",
            "images", "videos", "video_urls",
        ]

    def create(self, validated_data):
        images = validated_data.pop("images", [])
        videos = validated_data.pop("videos", [])
        video_urls = validated_data.pop("video_urls", [])

        with transaction.atomic():
            product = Product.objects.create(**validated_data)
            for i, img in enumerate(images):
                ProductImage.objects.create(product=product, image=img, is_primary=(i == 0))
            for v in videos:
                ProductVideo.objects.create(product=product, video=v)
            for url in video_urls:
                ProductVideo.objects.create(product=product, video_url=url)
        return product

    def update(self, instance, validated_data):
        for key in ("images", "videos", "video_urls"):
            validated_data.pop(key, None)
        return super().update(instance, validated_data)