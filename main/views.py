"""
room_booking/main/views.py
"""
from django.db.models import Avg, Min
from django.shortcuts import render

from hotels.models import Hotel


def index(request):
    hotels = (
        Hotel.objects
        .prefetch_related("images")
        .annotate(
            avg_rating=Avg("reviews__rating"),
            min_price=Min("room_types__price"),
        )
        .filter(avg_rating__isnull=False)
        .order_by("-avg_rating")[:9]
    )

    return render(request, "main/index.html", {"hotels": hotels})