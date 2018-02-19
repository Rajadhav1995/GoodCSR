from django.conf.urls import include, url
from django.contrib import admin
from dashboard.project_wall import get_project_updates



urlpatterns = [
    url(r'^updates/$',get_project_updates),
]
