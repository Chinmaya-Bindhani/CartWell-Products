from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug= models.SlugField(unique=True,blank=True)
    parent = models.ForeignKey("self",null=True,blank=True,on_delete=models.CASCADE,related_name="children")

    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args,**kwargs)

    def __str__(self):
        return  self.name

    class Meta:
        verbose_name_plural = "categories"


@receiver([post_save, post_delete], sender=Category)
def clear_category_cache(sender, **kwargs):
    cache.delete("categories:all")

class Product(models.Model):
    category = models.ForeignKey(Category,on_delete=models.PROTECT,related_name="products")
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100,db_index=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(1)])
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    sku = models.CharField(max_length=50 , unique=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    seller_id = models.PositiveIntegerField(
        db_index=True,
        null=True,
        blank=True
    )


    def __str__(self):
        return self.name
    class Meta:
        ordering = ["-created_at"]


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    is_primary = models.BooleanField(default=False)

class ProductVideo(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="videos")
    video = models.FileField(upload_to="product_videos/", blank=True, null=True)
    video_url = models.URLField(blank=True)   #YouTub
    title = models.CharField(max_length=150, blank=True)


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user_id = models.PositiveIntegerField()
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("product", "user_id")

@receiver([post_save, post_delete], sender=Product)
def clear_product_cache(sender, instance, **kwargs):
    cache.delete(f"product:{instance.pk}")

@receiver([post_save, post_delete], sender=ProductImage)
@receiver([post_save, post_delete], sender=ProductVideo)
def clear_product_cache_on_media(sender, instance, **kwargs):
    cache.delete(f"product:{instance.product_id}")