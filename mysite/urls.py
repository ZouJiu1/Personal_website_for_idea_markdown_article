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
    path("zhihu/", include("zhihu.urls")),
    path("zhihu/notify_edit", include("zhihu.urls")),
    path("think/", include("think.urls")),
    path("think/post_think", include("think.urls")),
    path("think/delete", include("think.urls")),
    path("think/uploadImg", include("think.urls")),
    path("think/detail", include("think.urls")),
    path("think/placeTop", include("think.urls")),
    path("video", include("video.urls")),
    path("video/uploadMedia", include("video.urls")),
    path("markdown_detail/",include("markdown_detail.urls")),
    path("markdown_detail/placeTop",include("markdown_detail.urls")),
    path("travel/", include("travel.urls")),
    path("travel/post_travel", include("travel.urls")),
    path("upload_video/", include("upload_video.urls")),
    
]
