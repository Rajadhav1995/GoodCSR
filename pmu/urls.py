"""pmu URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from views import (dashboard,user_information)
from views.user_information import (UserInformationStorage,)
from views.login import (signin,signout)
from projectmanagement.manage_roles import (projectuserslist,projectuseradd,
                                            projectuseredit,)
admin.autodiscover()

roles_patterns = ([
    url(r'^project/role/list/$',projectuserslist),
    url(r'^project/role/add/$',projectuseradd),
    url(r'^project/role/edit/$',projectuseredit),
])


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^dashboard/$',dashboard.admin_dashboard),
    url(r'^project/',include('projectmanagement.urls')),
    url(r'^upload/',include('media.urls')),
    url(r'^$',signin),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^dashboard/$',dashboard.admin_dashboard),
    url(r'^managing/',include('taskmanagement.urls')),
    url(r'^manage/user-access/$',UserInformationStorage.as_view()),
    url(r'^logout/$',signout),
    url(r'^manage/', include(roles_patterns)),

]

