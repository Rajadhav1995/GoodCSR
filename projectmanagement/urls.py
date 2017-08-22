from django.conf.urls import include, url
from django.contrib import admin
from projectmanagement.views import (create_project,project_list,project_detail,project_mapping,
									budget_tranche,)

urlpatterns = [
    url(r'^add/$',create_project),
    url(r'^list/$',project_list),
    url(r'^detail/$',project_detail),
    url(r'^mapping/$',project_mapping),
    url(r'^budget/tranche/$',budget_tranche),
]