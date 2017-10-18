from django.conf.urls import include, url
from django.contrib import admin
from media.views import list_document,timeline_upload,upload_attachment,edit_attachment,city_list


urlpatterns = [
    url(r'^doc/$',upload_attachment),
    url(r'^edit/$',edit_attachment),
    url(r'^list/$',list_document),
    url(r'^images/$',timeline_upload),
    url(r'^city-list/$',city_list),
]
