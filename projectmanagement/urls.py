from django.conf.urls import include, url
from django.contrib import admin
from projectmanagement.views import create_project,project_list

urlpatterns = [
    url(r'^add/$',create_project),
    url(r'^list/$',project_list),
]