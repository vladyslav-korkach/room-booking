from django import forms
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
    

class HotelSearchForm(forms.Form):
    city = forms.CharField(required=True)
    check_in = forms.DateField(required=True)
    check_out = forms.DateField(required=True)
    adults = forms.IntegerField(min_value=1, initial=1)
    children = forms.IntegerField(min_value=0, initial=0)


class HotelSearchListView(ListView):
    model = Hotel
    template_name = "hotels/search_results.html"
    context_object_name = "hotels"
    paginate_by = 6

    def get_queryset(self):
        self.form = HotelSearchForm(self.request.GET or None)

        if not self.form.is_valid():
            return Hotel.objects.none()
        
        queryset = (
            Hotel.objects
            .prefetch_related("images")
            .annotate(
                    avg_rating=Avg("reviews__rating"),
                    min_price=Min("room_types__price"),
                )
                .filter(avg_rating__isnull=False)
                
        )

        city = self.form.cleaned_data.get("city")
        adults = self.form.cleaned_data.get("adults") or 1
        children = self.form.cleaned_data.get("children") or 0

        total_guests = adults + children

        if city:
            queryset = queryset.filter(city__icontains=city)

        queryset = queryset.filter(room_types__capacity__gte=total_guests).distinct()

        return queryset.order_by("-avg_rating", "-id")
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = getattr(self, "form", HotelSearchForm())
        return context