"""
room_booking/booking/urls.py
"""
from django.urls import path
from .views import (
    BookingCreateModel, 
    BookingSuccessView, 
    MyBookingListView,
    CancelBookingView
)


urlpatterns = [
    path(
        "<slug:hotel_slug>/rooms/<slug:slug>/book/", 
        BookingCreateModel.as_view(), 
        name="booking_create"
    ),
    path("success/", BookingSuccessView.as_view(), name="booking_success"),
    path("my/", MyBookingListView.as_view(), name="my_bookings"),
    path("<int:pk>/cancel/", CancelBookingView.as_view(), name="booking_cancel"),

]