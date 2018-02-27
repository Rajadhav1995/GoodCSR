import pytz
import requests,ast
from ast import literal_eval
from itertools import chain
from django import template
register = template.Library()
from datetime import datetime
from media.models import Comment,Attachment
from django.contrib.contenttypes.models import ContentType
from taskmanagement.models import Task,Activity
from budgetmanagement.models import *
from projectmanagement.models import Project,UserProfile,ProjectFunderRelation,ProjectParameter
from pmu.settings import PMU_URL,SAMITHA_URL
from django.db.models import Max
from taskmanagement.views import ExpectedDatesCalculator 
import datetime

#    The dict type has been reimplemented to use a more compact representation based on a proposal by Raymond Hettinger and similar to the PyPy dict implementation. This resulted in dictionaries using 20% to 25% less memory when compared to Python 3.5.
#    Customization of class creation has been simplified with the new protocol.
#    The class attribute definition order is now preserved.
#    The order of elements in **kwargs now corresponds to the order in which keyword arguments were passed to the function.
#    DTrace and SystemTap probing support has been added.
#    The new PYTHONMALLOC environment variable can now be used to debug the interpreter memory allocation and access errors.

#Significant improvements in the standard library:

#    The asyncio module has received new features, significant usability and performance improvements, and a fair amount of bug fixes. Starting with Python 3.6 the asyncio module is no longer provisional and its API is considered stable.
#    A new file system path protocol has been implemented to support path-like objects. All standard library functions operating on paths have been updated to work with the new protocol.
#    The datetime module has gained support for Local Time Disambiguation.
#    The typing module received a number of improvements.
#    The tracemalloc module has been significantly reworked and is now used to provide better output for ResourceWarning as well as provide better diagnostics for memory allocation errors. See the PYTHONMALLOC section for more information.

#Security improvements:

#    The new secrets module has been added to simplify the generation of cryptographically strong pseudo-random numbers suitable for managing secrets such as account authentication, tokens, and similar.
#    On Linux, os.urandom() now blocks until the system urandom entropy pool is initialized to increase the security. See the PEP 524 for the rationale.
#    The hashlib and ssl modules now support OpenSSL 1.1.0.
#    The default settings and feature set of the ssl module have been improved.
#    The hashlib module received support for the BLAKE2, SHA-3 and SHAKE hash algorithms and the scrypt() key derivation function.

def get_delay_difference(tasks):
    diff = None
    today = datetime.datetime.now().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata'))
    if tasks:
        task_obj = tasks.reverse()[0]
        ExpectedDatesCalculator(task=task_obj)
        planned_end = task_obj.end_date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata'))
        planned_start = task_obj.start_date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata'))
        expected_end = task_obj.expected_end_date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata'))
        diff = (expected_end - planned_date).days
        if today > planned_start:
            maxi = int(-(diff))
        elif diff ==0 and obj.status ==2:
            maxi = 0
        else:
            maxi = diff
    return maxi


def get_cat_delay_point(obj,key):
    diff = None
    if key == 'cat':
        activities= Activity.objects.filter(super_category = obj)
        tasks = Task.objects.filter(activity__super_category = obj).order_by('end_date')
        high_task = tasks.reverse()[0]
        diff = get_max_diff_tasks(high_task)
#        for i in activities:
#            tasks = Task.objects.filter(activity=i).order_by('end_date')
#            max_diff = get_delay_difference(tasks)
#            if diff < max_diff:
#                diff = max_diff
    else:
        act_obj = Activity.objects.get_or_none(id=obj.id)
        tasks = Task.objects.filter(activity = act_obj).order_by('end_date')
        diff = get_delay_difference(tasks)
        
    slug = str(obj.slug)
    return diff,slug

def get_max_diff_tasks(obj):
    today = datetime.datetime.now().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata'))
    ExpectedDatesCalculator(task=obj)
    planned_date = obj.end_date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata'))
    expected_end = obj.expected_end_date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata'))
    planned_start = obj.start_date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata'))
    diff = (expected_end - planned_date).days
    if today > planned_start:
        maxi = int(-(diff))
    elif diff ==0 and obj.status ==2:
        maxi = 0
    else:
        maxi = diff
    return maxi

def get_task_delay_ponts(obj):
    maxi=''
    task_data_list = []
    tasks_obj = Task.objects.filter(activity=obj).order_by('end_date')
    for i in tasks_obj:
        maxi=0
        task_data={}
        maxi = get_max_diff_tasks(i)
        task_data['name']=str(i.name)
        task_data['y']= maxi
        task_data['task_progress']= str(i.task_progress)
        task_data_list.append(task_data)
    return task_data_list

def get_activity_delay_point(super_obj):
    data = []
    act_list = {}
    data_task=[]
    activities = Activity.objects.filter(super_category = super_obj)
    for obj in activities:
        act_list = {}
        task_list={}
        act_list['name'] = str(obj.name)
        act_list['y'],act_list['drilldown'] = get_cat_delay_point(obj,key='acti')
        task_list['id'] = act_list['drilldown']
        task_list['name'] = 'Task'
        task_list['color'] = '#006C90'
        task_list['data'] = get_task_delay_ponts(obj)
        data_task.append(task_list)
        data.append(act_list)
    return data,data_task
        
from collections import OrderedDict
@register.assignment_tag
def super_category_delay(project_slug):
    series = []
    act_dict = OrderedDict()
    cat_dict ={}
    project_obj = Project.objects.get_or_none(slug=project_slug)
    super_list = SuperCategory.objects.filter(project=project_obj).exclude(parent=None)
    delay_list =[]
    for obj in super_list:
        cat_dict ={}
        act_dict={'id':'','name':'Activity','color':'#006C90','data':[]}
        cat_dict['name']=str(obj.name)
        cat_dict['y'],cat_dict['drilldown']=get_cat_delay_point(obj,key='cat')
        delay_list.append(cat_dict)
        act_dict['id'] = cat_dict['drilldown']
        act_dict['data'],task_details= get_activity_delay_point(obj)
        series.append(act_dict)
        for i in task_details:
            series.append(i)
    import json
    return json.dumps(delay_list),json.dumps(series)
    

