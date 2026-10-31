from django.urls import path

from . import views

urlpatterns = [
    path("index", views.index, name="index"),
    # path("detail", views.detail, name="detail"),
    path("post_travel", views.post_travel, name="post_travel"),
    # path("uploadImg", views.uploadImg, name="uploadImg"),
    path("delete", views.delete, name="delete"),
]