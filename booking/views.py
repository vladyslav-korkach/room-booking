from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, TemplateView, ListView
from django.urls import reverse
from .models import Booking
from .forms import BookingForm
from hotels.models import RoomType
from django.views import View
from django.contrib import messages
from django.utils import timezone



class BookingCreateModel(CreateView):
    model = Booking
    form_class = BookingForm
    template_name = "booking/booking_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.room_type = get_object_or_404(
            RoomType.objects.select_related("hotel"),
            hotel__slug=self.kwargs["hotel_slug"],
            slug=self.kwargs["slug"],
        )
        return super().dispatch(request, *args, **kwargs)
    

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["room_type"] = self.room_type
        return kwargs
    

    def get_initial(self):
        initial = super().get_initial()

        if self.request.GET.get("check_in"):
            initial["check_in"] = self.request.GET["check_in"]

        if self.request.GET.get("check_out"):
            initial["check_out"] = self.request.GET["check_out"]

        if self.request.GET.get("adults"):
            initial["guests"] = self.request.GET["adults"]

        if self.request.user.is_authenticated:
            initial["full_name"] = (
                self.request.user.get_full_name() or self.request.user.username
            )
            initial["email"] = self.request.user.email

        return initial
    

    def form_valid(self, form):
        form.instance.room_type = self.room_type
        if self.request.user.is_authenticated:
            form.instance.user = self.request.user
            if not form.cleaned_data.get("full_name"):
                form.instance.full_name = self.request.user.get_full_name() or self.request.user.username
            if not form.cleaned_data.get("email"):
                form.instance.email = self.request.user.email
        return super().form_valid(form)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["room_type"] = self.room_type
        context["hotel"] = self.room_type.hotel
        return context

    
    def get_success_url(self):
        return reverse("booking_success")


class BookingSuccessView(TemplateView):
    template_name = "booking/success.html"
    login_url = "login"


class MyBookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "booking/my_booking.html"
    context_object_name = "bookings"
    paginate_by = 10
    login_url = "login"

    def get_queryset(self):
        return (
            Booking.objects
            .select_related("room_type", "room_type__hotel")
            .filter(user=self.request.user)
            .order_by("-created_at")
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["today"] = timezone.localdate()
        return context
    

class CancelBookingView(LoginRequiredMixin, View):
    login_url = "login"

    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk, user=request.user)
        if booking.status == Booking.Status.CANCELED:
            messages.info(request, "Booking is already canceled.")
            return redirect("my_bookings")
        
        if timezone.localdate() >= booking.check_in:
            messages.error(request, "You cannot cancel a booking after check-in date.")
            return redirect("my_bookings")
        
        booking.status = Booking.Status.CANCELED
        booking.save(update_fields=["status"])
        messages.success(request, "Booking canceled.")

        return redirect("my_bookings")
