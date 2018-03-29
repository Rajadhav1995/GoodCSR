from django.conf.urls import include, url
from django.contrib import admin
from projectmanagement.views import (create_project,project_list,
    budget_tranche,key_parameter,tranche_list,add_parameter,edit_parameter,
    upload_parameter,manage_parameter,manage_parameter_values,project_summary,
    delete_upload_image,remove_record,)
from projectmanagement.manage_roles import manage_funder_relation

# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
urlpatterns = [
    url(r'^add/$',create_project),
    url(r'^list/$',project_list),
    url(r'^budget/tranche/$',budget_tranche),
    url(r'^upload/key-parameter/$',key_parameter),
    url(r'^tranche/list/$',tranche_list),
    url(r'^parameter/add/$',add_parameter),
    url(r'^upload/parameter/value/$',upload_parameter),
    url(r'^parameter/manage/$',manage_parameter),
    url(r'^parameter/values/manage/$',manage_parameter_values),
    url(r'^summary/$',project_summary),
    url(r'^parameter/edit/$',edit_parameter),
    url(r'^delete/upload/image/$',delete_upload_image),
    url(r'^remove/record/$',remove_record),
    url(r'^manage/funder/$',manage_funder_relation),
]
# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.