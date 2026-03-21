"""
room_booking/booking/urls.py
"""
from django.urls import path
from .views import BookingCreateModel, BookingSuccessView

urlpatterns = [
    path(
        "<slug:hotel_slug>/rooms/<slug:slug>/book/", 
        BookingCreateModel.as_view(), 
        name="booking_create"
    ),
    path("success/", BookingSuccessView.as_view(), name="booking_success"),
]