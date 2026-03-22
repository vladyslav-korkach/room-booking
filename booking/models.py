from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from hotels.models import RoomType

class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELED = "canceled", "Canceled"
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
        null=True,
        blank=True,
    )

    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name="bookings")

    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50)

    check_in = models.DateField()
    check_out = models.DateField()

    guests = models.PositiveIntegerField()

    status = models.CharField(
        max_length=120,
        choices=Status.choices,
        default=Status.PENDING,
    )

    created_at = models.DateTimeField(auto_now_add=True)


    def clean(self):
        if self.check_out <= self.check_in:
            raise ValidationError("Check-out must be after check-in")
        
        if self.guests > self.room_type.capacity:
            raise ValidationError("Too many guests for this room type")
        

    def __str__(self):
        return f"{self.full_name} - {self.room_type} ({self.check_in} → {self.check_out})"
