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
from views.user_information import (UserInformationStorage,)
from views.login import (signin,signout,homepage)
from views.homepage import (feedback,email_validation)
from projectmanagement.manage_roles import (projectuserslist,projectuseradd,
                                            projectuseredit)
from budgetmanagement.manage_budget import (projectbudgetadd,projectbudgetlist,
                                            projectbudgetcategoryadd,projectlineitemadd,
                                            projectbudgetdetail,budgetutilization,
                                            budgetview,year_quarter_list,
                                            budgetlineitemedit)
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
    url(r'^project/budget/lineitem/edit/$',budgetlineitemedit),

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
    url(r'^feedback/$',feedback),
    url(r'^email-valid/$',email_validation),
    url(r'^managing/$',include('taskmanagement.urls')),
    url(r'^managing/',include('taskmanagement.urls')),
    url(r'^manage/user-access/$',UserInformationStorage.as_view()),
    url(r'^logout/$',signout),
    url(r'^manage/', include(roles_patterns)),

]

