from django.conf.urls import include, url
from django.contrib import admin
from projectmanagement.views import upload_attachment,edit_attachment


urlpatterns = [
    url(r'^doc/$',upload_attachment),
    url(r'^edit/$',edit_attachment),
]