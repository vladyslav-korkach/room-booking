from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify

class Hotel(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    city = models.CharField(max_length=120)
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    stars = models.PositiveSmallIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )

    @property
    def main_image(self):
        return self.images.filter(is_main=True).first()
    
    @property
    def rating(self):
        reviews = self.reviews.all()
        if not reviews.exists():
            return None
        return round(sum(review.rating for review in reviews) / reviews.count(), 1)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Hotel.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
            
            self.slug = slug
        super().save(*args, **kwargs)
        

    def __str__(self):
        return self.name
    

class RoomType(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="room_types")
    name = models.CharField(max_length=120)
    slug = models.SlugField(blank=True)
    capacity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_quantity = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)


    @property
    def main_image(self):
        return self.images.filter(is_main=True).first()
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while RoomType.objects.filter(hotel=self.hotel, slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.hotel.name} - {self.name}"
    
    class Meta:
        unique_together = ("hotel", "slug")
    

class HotelImage(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="images")
    image = models.CharField(max_length=512, blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    is_main = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_main"]

    def __str__(self):
        return f"Image for {self.hotel.name}"
    

class RoomTypeImage(models.Model):
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name="images")
    image = models.CharField(max_length=512, blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    is_main = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_main"]

    def __str__(self):
        return f"Image for {self.room_type.name}"
    

class HotelReview(models.Model):
    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    author_name = models.CharField(max_length=120)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.hotel.name} - {self.rating}/10"  