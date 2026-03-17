from django.shortcuts import render
from django.views.generic import ListView
from django.db.models import Avg, Min
from hotels.models import Hotel

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


