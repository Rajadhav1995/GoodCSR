"""pmu URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from views import (dashboard,user_information)
from views.user_information import (UserInformationStorage,saveimage)
from views.login import (signin,signout,homepage,login_popup)
from views.homepage import (feedback,email_validation)
from projectmanagement.manage_roles import (projectuserslist,projectuseradd,
                                            projectuseredit)
from budgetmanagement.manage_budget import (projectbudgetadd,projectbudgetlist,
                                            projectbudgetcategoryadd,projectlineitemadd,
                                            projectbudgetdetail,budgetutilization,
                                            budgetview,year_quarter_list,
                                            budgetlineitemedit,month_quarter_list,
                                            category_listing,category_add,
                                            delete_category,)
from userprofile.views import *
import userprofile
from django.conf.urls import handler404, handler500

handler404 = userprofile.views.handler404
handler500 = userprofile.views.handler500

admin.autodiscover()

roles_patterns = ([
    url(r'^project/role/list/$',projectuserslist),
    url(r'^project/role/add/$',projectuseradd),
    url(r'^project/role/edit/$',projectuseredit),
    url(r'^project/budget/list/$',projectbudgetlist),
    url(r'^project/budget/create/$',projectbudgetadd),
    url(r'^project/budget/category/add/$',projectbudgetcategoryadd),
    url(r'^project/budget/lineitem/add/$',projectlineitemadd),
    url(r'^project/budget/detail/$',projectbudgetdetail),
    url(r'^project/budget/report-utilization/$',budgetutilization),
    url(r'^project/budget/view/$',budgetview),
    url(r'^quarter/list/$',year_quarter_list),
    url(r'^month/list/$',month_quarter_list),
    url(r'^project/budget/lineitem/edit/$',budgetlineitemedit),
    url(r'^project/budget/category/listing/$',category_listing),
    url(r'^project/budget/add/category/$',category_add),
    url(r'^project/budget/category/delete/$',delete_category),

])

userroles_patterns = ([

    url(r'^list/(?P<model>(:?user|role|menu))/$', UserListView.as_view()),
    url(r'^list/(?P<model>(:?roleconfig))/(?P<pid>\d+)/$', UserListView.as_view()),
    url(r'^add/(?P<model>(:?role|user|menu))/$', UserAddView.as_view()),
    url(r'^add/(?P<model>(:?roleconfig))/(?P<pid>\d+)/$', UserAddView.as_view()),
    url(r'^edit/(?P<model>(:?role|user|menu|roleconfig))/(?P<pk>\d+)/$', UserEditView.as_view()),
    url(r'^edit/(?P<model>(:?roleconfig))/(?P<pk>\d+)/(?P<pid>\d+)/$', UserEditView.as_view()),
    url(r'^active/(?P<model>(:?role|user|menu|roleconfig))/(?P<pk>\d+)/$', UserActive.as_view()),
    url(r'^active/(?P<model>(:?roleconfig))/(?P<pk>\d+)/(?P<pid>\d+)/$', UserActive.as_view()),
    url(r'^manage/role/(?P<pk>\d+)/$', manage_role),
    url(r'^manage/menu/(?P<pk>\d+)/$', manage_menu),
    url(r'^manage/active/(?P<pk>\d+)/$', active),

])


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^dashboard/$',dashboard.admin_dashboard),
    url(r'^project/',include('projectmanagement.urls')),
    url(r'^upload/',include('media.urls')),
    url(r'^report/',include('budgetmanagement.report_urls')),
    url(r'^login/$',signin),
    url(r'^$',homepage),
    url(r'^login-popup/$',login_popup),
    url(r'^feedback/$',feedback),
    url(r'^email-valid/$',email_validation),
    url(r'^managing/',include('taskmanagement.urls')),
    url(r'^manage/user-access/$',UserInformationStorage.as_view()),
    url(r'^logout/$',signout),
    url(r'^save/image/$',saveimage),
    url(r'^manage/', include(roles_patterns)),
    url(r'^usermanagement/',include(userroles_patterns)),

]

