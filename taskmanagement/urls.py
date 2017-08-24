from django.conf.urls import url
from .views import *
from .forms import *


urlpatterns = [
    url(r'^(?P<model_name>.*)/listing/$',listing),
    url(r'^(?P<model_name>[\w-]+)/(?P<m_form>[\w-]+)/add/',add_taskmanagement),
    url(r'^(?P<model_name>[\w-]+)/(?P<m_form>[\w-]+)/edit/(?P<slug>.+)/$',edit_taskmanagement),
    url(r'^(?P<model_name>[\w-]+)/status/',active_change),
    url(r'^task/dependencies/$',task_dependencies),
    url(r'^milestone/overdue/$',milestone_overdue),
    url(r'^tasks/auto-computation/date/$',task_auto_computation_date),
    url(r'^total/tasks/completed/$',total_tasks_completed),
]
