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

def get_cat_delay_point(obj):
    import datetime
    diff=0
    max_list = []
    today = datetime.datetime.now()
    
    task_list = Task.objects.filter(activity__super_category=obj)
#    ExpectedDatesCalculator(task_list=tasks)
    for i in task_list:
        if i.actual_end_date :
            max_list.append(i.actual_end_date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata')))
        else:
            max_list.append(i.end_date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata')))
    max_end = max(max_list)
    diff = (max_end.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata')) - today.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata'))).days
    slug = str(obj.slug)
    return diff,slug

@register.assignment_tag
def super_category_delay(project_slug):
    cat_dict ={}
    project_obj = Project.objects.get_or_none(slug=project_slug)
    super_list = SuperCategory.objects.filter(project=project_obj).exclude(parent=None)
    delay_list =[]
    for obj in super_list:
        cat_dict ={}
        cat_dict['name']=str(obj.name)
        cat_dict['y'],cat_dict['drilldown']=get_cat_delay_point(obj)
        delay_list.append(cat_dict)
    
    return delay_list
