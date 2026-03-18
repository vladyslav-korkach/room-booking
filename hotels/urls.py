from django.urls import path
from . import views
from .views import HotelListView, HotelDetailView, RoomTypeDetailView

urlpatterns = [
    path("", HotelListView.as_view(), name="hotels"),
    path("<slug:slug>/", HotelDetailView.as_view(), name="hotel_detail"),
    path("<slug:hotel_slug>/rooms/<slug:slug>/", RoomTypeDetailView.as_view(), name="room_type_detail")
]
