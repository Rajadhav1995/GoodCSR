from django.conf.urls import url
from .views import *
from .forms import *


urlpatterns = [
    url(r'^(?P<model_name>.*)/listing/$',listing),
    url(r'^(?P<model_name>[\w-]+)/(?P<m_form>[\w-]+)/add/',add_taskmanagement),
    url(r'^(?P<model_name>[\w-]+)/(?P<m_form>[\w-]+)/edit/(?P<slug>.+)/$',edit_taskmanagement),
    url(r'^(?P<model_name>[\w-]+)/status/',active_change),
    url(r'^task/start-date/$',task_start_date),
    url(r'^milestone/overdue/$',milestone_overdue),
]
