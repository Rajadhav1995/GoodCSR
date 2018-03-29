from django.conf.urls import url
from .views import *
from .forms import *

# URLS for Task management
# 
urlpatterns = [
#    url(r'^(?P<model_name>.*)/listing/$',listing),
    url(r'^listing/$',listing),
#    url(r'^tasks/updates/(?P<obj_id>.*)/(?P<slug>.*)/$',taskdateupdates),
    url(r'^(?P<model_name>[\w-]+)/(?P<m_form>[\w-]+)/add/$',add_taskmanagement),
    url(r'^(?P<model_name>[\w-]+)/(?P<m_form>[\w-]+)/edit/(?P<slug>.+)/$',edit_taskmanagement),
    url(r'^(?P<model_name>[\w-]+)/status/',active_change),
    url(r'^task/dependencies/$',task_dependencies),
    url(r'^milestone/overdue/$',milestone_overdue),
    url(r'^tasks/auto-computation/date/$',task_auto_computation_date),
    url(r'^my-tasks/details/$',my_tasks_details),
    url(r'^my-calendar/details/$',my_tasks_details),
    url(r'^tasks/expected-date/caluclator/$',get_tasks_objects),
    url(r'^gantt-chart-data/$', GanttChartData.as_view()),
    #url(r'^my-tasks/updates/(?P<obj_id>.*)$',task_comments),
    url(r'^my-tasks/updates/$',task_comments),
    url(r'^activites/$',get_activites_list),
    url(r'supercategories/selected/$',get_super_selected),
    url(r'activities/selected/$',get_activity_selected),
    url(r'^activity/related/tasks/$',get_activity_tasks),
#    url(r'^tasks/maximum/end_date/$',tasks_max_end_date),
    
#    url(r'^tasks/updates/(?P<obj_id>.*)/$',taskdateupdates),
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