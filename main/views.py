"""
room_booking/main/views.py
"""
from django.db.models import Avg, Min
from django.shortcuts import render
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import SignUpForm
from hotels.models import Hotel, RoomType
from hotels.views import HotelSearchForm


def index(request):
    hotels = list(
        Hotel.objects
        .prefetch_related("images")
        .annotate(
            avg_rating=Avg("reviews__rating"),
            min_price=Min("room_types__price"),
        )
        .filter(avg_rating__isnull=False)
        .order_by("-avg_rating")[:9]
    )

    context = {
        "hotels": hotels,
        "hotel_count": Hotel.objects.count(),
        "city_count": Hotel.objects.values("city").distinct().count(),
        "room_type_count": RoomType.objects.count(),
        "search_form": HotelSearchForm(),
    }

    return render(request, "main/index.html", context)


class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("my_bookings")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response
