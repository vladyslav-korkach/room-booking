from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Min
from hotels.models import Hotel, RoomType

class HotelListView(ListView):
    paginate_by = 6
    model = Hotel
    template_name = "hotels/list.html"
    context_object_name = "hotels"

    def get_queryset(self):
        return (
            Hotel.objects
                .prefetch_related("images")
                .annotate(
                    avg_rating=Avg("reviews__rating"),
                    min_price=Min("room_types__price"),
                )
                .filter(avg_rating__isnull=False)
                .order_by("-id")
        )


class HotelDetailView(DetailView):
    model = Hotel
    template_name = "hotels/detail.html"
    context_object_name = "hotel"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return (
            Hotel.objects.prefetch_related(
                "images",
                "reviews",
                "room_types",
                "room_types__images",
            )
            .annotate(
                avg_rating=Avg("reviews__rating"),
                min_price=Min("room_types__price"),
            )
        )
    

class RoomTypeDetailView(DetailView):
    model = RoomType
    template_name = "hotels/room_type_detail.html"
    context_object_name = "room_type"

    def get_queryset(self):
        return (
            RoomType.objects
            .select_related("hotel")
            .prefetch_related("images", "hotel__images")
        )

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        
        return get_object_or_404(
            queryset,
            hotel__slug=self.kwargs["hotel_slug"],
            slug=self.kwargs["slug"],
        )