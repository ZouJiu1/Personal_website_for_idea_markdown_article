"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path("csdn/", include("csdn.urls")),
    path("csdn/postArticle", include("csdn.urls")),
    path("csdn/delete", include("csdn.urls")),
    path("csdn/editArticle", include("csdn.urls")),
    path("csdn/uploadImg", include("csdn.urls")),
    path("csdn/renzheng", include("csdn.urls")),
    path("csdn/getPrimaryText", include("csdn.urls")),
    path("csdn/clickpage", include("csdn.urls")),
    path("csdn/register", include("csdn.urls")),
    path("csdn/sendverify", include("csdn.urls")),
    path("csdn/login", include("csdn.urls")),
    path("csdn/getusername", include("csdn.urls")),
    path("csdn/mainpagedataget", include("csdn.urls")),
    path("csdn/mainpageuploadImg", include("csdn.urls")),
    path("csdn/FormsubmitSetting", include("csdn.urls")),
    path("csdn/GetSetting", include("csdn.urls")),
    path("csdn/placeTopTop", include("csdn.urls")),
    path("csdn/cancelPlaceTopTop", include("csdn.urls")),
    path("csdn/NicknameSetting", include("csdn.urls")),
    path("csdn/themeChange", include("csdn.urls")),
    path("csdn/getThemeColor", include("csdn.urls")),
    path("csdn/upvote_change", include("csdn.urls")),
    path("csdn/comment_add", include("csdn.urls")),
    path("csdn/kshoucang", include("csdn.urls")),
    
    path("zhihu/", include("zhihu.urls")),
    path("zhihu/notify_edit", include("zhihu.urls")),
    path("think/", include("think.urls")),
    path("think/post_think", include("think.urls")),
    path("think/delete", include("think.urls")),
    path("think/uploadImg", include("think.urls")),
    path("think/detail", include("think.urls")),
    path("think/placeTop", include("think.urls")),
    path("think/cancelPlaceTop", include("think.urls")),
    path("think/upvote_change", include("think.urls")),
    path("think/comment_add", include("think.urls")),
    path("think/kshoucang", include("think.urls")),
    path("think/modify", include("think.urls")),

    path("video/", include("video.urls")),
    path("video/uploadMedia", include("video.urls")),
    path("markdown_detail/",include("markdown_detail.urls")),
    path("travel/", include("travel.urls")),
    path("travel/post_travel", include("travel.urls")),
    path("travel/delete", include("travel.urls")),
    path("upload_video/", include("upload_video.urls")),
    path("upload_video/upload", include("upload_video.urls")),
    path("upload_video/delete", include("upload_video.urls")),

    path("commonuse/", include("commonuse.urls")),
    path("commonuse/getfiledata", include("commonuse.urls")),
    path("commonuse/submitAddwebsite", include("commonuse.urls")),
    path("commonuse/getbingimg", include("commonuse.urls")),
    path("commonuse/downloadall", include("commonuse.urls")),
    
]
