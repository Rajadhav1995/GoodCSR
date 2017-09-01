from django.conf.urls import include, url
from django.contrib import admin
from projectmanagement.views import upload_attachment,edit_attachment
from media.views import list_document,timeline_upload


urlpatterns = [
    url(r'^doc/$',upload_attachment),
    url(r'^edit/$',edit_attachment),
    url(r'^list/$',list_document),
    url(r'^images/$',timeline_upload),
]
