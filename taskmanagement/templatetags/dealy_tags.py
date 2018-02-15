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

def get_delay_difference(tasks):
    diff = ''
    today = datetime.datetime.now().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata'))
    if tasks:
        task_obj = tasks.reverse()[0]
        if task_obj.actual_end_date:
            max_end = task_obj.actual_end_date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata'))
        else:
            ExpectedDatesCalculator(task=task_obj)
            max_end = task_obj.expected_end_date
        diff = (max_end - today).days
    return diff

def get_cat_delay_point(obj,key):
    if key == 'cat':
        tasks = Task.objects.filter(activity__super_category=obj).order_by('end_date')
    else:
        tasks = Task.objects.filter(activity=obj).order_by('end_date')
    diff = get_delay_difference(tasks)
    slug = str(obj.slug)
    return diff,slug

def get_task_delay_ponts(obj):
    task_data_list = []
    today = datetime.datetime.now().replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata'))
    tasks_obj = Task.objects.filter(activity=obj).order_by('end_date')
    for i in tasks_obj:
        task_data={}
        if i.actual_end_date:
            max_end = i.actual_end_date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata'))
        else:
            ExpectedDatesCalculator(task=i)
            max_end = i.expected_end_date
        diff = (max_end - today).days
        task_data['name']=str(i.name)
        task_data['y']= diff
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
    print series
    import json
    return json.dumps(delay_list),json.dumps(series)
