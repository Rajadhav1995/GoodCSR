from django.conf.urls import patterns, url
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.cache import never_cache

from ckeditor import views

#ckeditorurl to be written here
urlpatterns = patterns(
    '',
    url(r'^upload/', views.upload, name='ckeditor_upload'),
    url(r'^browse/', never_cache(staff_member_required(views.browse)), name='ckeditor_browse'),
)
