from django.conf.urls import include, url
from django.contrib import admin
from projectmanagement.views import (create_project,project_list,project_detail,project_mapping,
    budget_tranche,key_parameter,tranche_list,add_parameter,
    upload_parameter,manage_parameter,manage_parameter_values,project_summary,)
#from views.dashboard import project_summary

urlpatterns = [
    url(r'^add/$',create_project),
    url(r'^list/$',project_list),
    url(r'^detail/$',project_detail),
    url(r'^mapping/$',project_mapping),
    url(r'^budget/tranche/$',budget_tranche),
    url(r'^upload/key-parameter/$',key_parameter),
    url(r'^tranche/list/$',tranche_list),
    url(r'^parameter/add/$',add_parameter),
    url(r'^upload/parameter/value/$',upload_parameter),
    url(r'^parameter/manage/$',manage_parameter),
    url(r'^parameter/values/manage/$',manage_parameter_values),
    url(r'^summary/$',project_summary),
    
]
