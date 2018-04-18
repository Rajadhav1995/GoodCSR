# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
from django.conf.urls import include, url
from django.contrib import admin
from dashboard.project_wall import get_project_updates,create_note



urlpatterns = [
    url(r'^updates/$',get_project_updates),
    url(r'^add/note/$',create_note),
]

# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.