from django.urls import path

from . import views

urlpatterns = [
    path("index", views.index, name="index"),
    path("notify_edit", views.notify_edit, name="notify_edit"),
]