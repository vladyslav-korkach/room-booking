from django.urls import path
from . import views
from .views import HotelListView

urlpatterns = [
    path("", HotelListView.as_view(), name="hotels")
]
