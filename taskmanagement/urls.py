from django.conf.urls import url
from .views import *
from .forms import *


urlpatterns = [
#    url(r'^(?P<model_name>.*)/listing/$',listing),
    url(r'^listing/$',listing),
    url(r'^(?P<model_name>[\w-]+)/(?P<m_form>[\w-]+)/add/$',add_taskmanagement),
    url(r'^(?P<model_name>[\w-]+)/(?P<m_form>[\w-]+)/edit/(?P<slug>.+)/$',edit_taskmanagement),
    url(r'^(?P<model_name>[\w-]+)/status/',active_change),
    url(r'^task/dependencies/$',task_dependencies),
    url(r'^milestone/overdue/$',milestone_overdue),
    url(r'^tasks/auto-computation/date/$',task_auto_computation_date),
    url(r'^my-tasks/details/$',my_tasks_details),
    url(r'^tasks/expected-date/caluclator/$',get_tasks_objects),
    url(r'^gantt-chart-data/$', GanttChartData.as_view()),
    url(r'^my-tasks/updates/(?P<obj_id>.*)$',task_comments),
    url(r'^activites/$',get_activites_list),
    url(r'supercategories/selected/$',get_super_selected),
    url(r'activities/selected/$',get_activity_selected),
    url(r'^activity/related/tasks/$',get_activity_tasks),
    url(r'^tasks/maximum/end_date/$',tasks_max_end_date),
]
