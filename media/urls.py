from django.conf.urls import include, url
from django.contrib import admin
from media.views import list_document,timeline_upload,upload_attachment,edit_attachment,city_list

# URLs for media management
# 
# Django provides a range of tools and libraries 
# to help you build forms to accept input from 
# site visitors, and then process and respond to the input.
# Django provides a range of tools and libraries 
# to help you build forms to accept input from 
# site visitors, and then process and respond to the input.
urlpatterns = [
    url(r'^doc/$',upload_attachment),
    url(r'^edit/$',edit_attachment),
    url(r'^list/$',list_document),
    url(r'^images/$',timeline_upload),
    url(r'^city-list/$',city_list),
]

# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
