"""
room_booking/hotels/urls.py
"""
from django.urls import path
from . import views
from .views import HotelListView, HotelDetailView, RoomTypeDetailView, HotelSearchListView
from booking.views import BookingCreateModel

urlpatterns = [
    path("", HotelListView.as_view(), name="hotels"),
    path("search/", HotelSearchListView.as_view(), name="hotel_search"),
    path("<slug:hotel_slug>/rooms/<slug:slug>/", RoomTypeDetailView.as_view(), name="room_type_detail"),
    path("<slug:hotel_slug>/rooms/<slug:slug>/book/", BookingCreateModel.as_view(), name="booking_create"),
    path("<slug:slug>/", HotelDetailView.as_view(), name="hotel_detail"),
]

