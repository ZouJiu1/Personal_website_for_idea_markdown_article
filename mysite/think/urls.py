from django.urls import path

from . import views

urlpatterns = [
    path("index", views.index, name="index"),
    path("detail", views.detail, name="detail"),
    path("post_think", views.post_think, name="post_think"),
    path("uploadImg", views.uploadImg, name="uploadImg"),
    path("delete", views.delete, name="delete"),
    path("placeTop", views.placeTop, name="placeTop"),
    path("cancelPlaceTop", views.cancelPlaceTop, name="cancelPlaceTop"),
    path("upvote_change", views.upvote_change, name="upvote_change"),
    path("comment_add", views.comment_add, name="comment_add"),
    path("kshoucang", views.kshoucang, name="kshoucang"),
    path("modify", views.modify, name="modify"),
]