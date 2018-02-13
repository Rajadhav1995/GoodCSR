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
    today = datetime.datetime.now()
    task_list = Task.objects.filter(activity__super_category=obj).values_list('end_date',flat = True)
    if task_list:
        max_end = max(task_list)
        diff = (today - max_end).days
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
