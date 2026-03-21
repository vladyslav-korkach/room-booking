from django.views.generic import CreateView
from django.urls import reverse
from .models import Booking
from .forms import BookingForm
from hotels.models import RoomType
from django.views.generic import TemplateView


class BookingCreateModel(CreateView):
    model = Booking
    form_class = BookingForm
    template_name = "booking/booking_form.html"

    def get_room_type(self):
        if not hasattr(self, "_room_type"):
            self._room_type = RoomType.objects.select_related("hotel").get(
                slug=self.kwargs.get("slug"),
                hotel__slug=self.kwargs.get("hotel_slug")
            )
        return self._room_type

    def get_initial(self):
        initial = super().get_initial()

        if self.request.GET.get("check_in"):
            initial["check_in"] = self.request.GET["check_in"]

        if self.request.GET.get("check_out"):
            initial["check_out"] = self.request.GET["check_out"]

        if self.request.GET.get("adults"):
            initial["guests"] = self.request.GET["adults"]

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["room_type"] = self.get_room_type()
        return context

    def form_valid(self, form):
        form.instance.room_type = self.get_room_type()
        return super().form_valid(form)
    

    def get_success_url(self):
        return reverse("booking_success")


class BookingSuccessView(TemplateView):
    template_name = "booking/success.html"
