"""
room_booking/main/urls.py
"""
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="home"),
    path("benefits/", views.benefits, name="benefits"),
]
