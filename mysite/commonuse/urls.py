from django.urls import path

from . import views

urlpatterns = [
    path("index", views.index, name="index"),
    path("getfiledata", views.getfiledata, name="getfiledata"),
    path("submitAddwebsite", views.submitAddwebsite, name="submitAddwebsite"),
    path("getbingimg", views.getbingimg, name="getbingimg"),
    path("downloadall", views.downloadall, name="downloadall"),
]