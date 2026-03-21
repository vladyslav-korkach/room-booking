from django.db import models
from hotels.models import RoomType

class Booking(models.Model):
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name="bookings")

    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50)

    check_in = models.DateField()
    check_out = models.DateField()

    guests = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.room_type} ({self.check_in} → {self.check_out})"