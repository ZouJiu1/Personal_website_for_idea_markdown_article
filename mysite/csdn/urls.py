from django.urls import path

from . import views

urlpatterns = [
    path("index", views.index, name="index"),
    path("postArticle", views.postArticle, name="postArticle"),
    path("delete", views.delete_directory, name="delete"),
    path("editArticle", views.editArticle, name="editArticle"),
    path("uploadImg", views.uploadImg, name="uploadImg"),
    path("renzheng", views.renzheng, name="renzheng"),
    path("getPrimaryText", views.getPrimaryText, name="getPrimaryText"),
    path("clickpage", views.clickpage, name="clickpage"),
    path("register", views.register, name="register"),
    path("sendverify", views.sendverify, name="sendverify"),
    path("login", views.login, name="login"),
    path("getusername", views.getusername, name="getusername"),
    path("mainpagedataget", views.mainpagedataget, name="mainpagedataget"),
    path("mainpageuploadImg", views.mainpageuploadImg, name="mainpageuploadImg"),
    path("FormsubmitSetting", views.FormsubmitSetting, name="FormsubmitSetting"),
    path("GetSetting", views.GetSetting, name="GetSetting"),
    path("placeTopTop", views.placeTopTop, name="placeTopTop"),
    path("NicknameSetting", views.NicknameSetting, name="NicknameSetting"),
    path("themeChange", views.themeChange, name="themeChange"),
    path("getThemeColor", views.getThemeColor, name="getThemeColor"),
    path("upvote_change", views.upvote_change, name="upvote_change"),
    path("comment_add", views.comment_add, name="comment_add"),
    path("kshoucang", views.kshoucang, name="kshoucang"),
]