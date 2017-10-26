import requests,ast
import datetime
import json
from django import template
from django.db.models import Sum
from datetime import datetime
from dateutil import relativedelta
from itertools import chain
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from pmu.settings import (SAMITHA_URL,PMU_URL)
from projectmanagement.models import (Project, UserProfile,ProjectFunderRelation)
from budgetmanagement.models import (Budget,ProjectBudgetPeriodConf,BudgetPeriodUnit,Question,Block)
from media.models import (Comment,)
from userprofile.models import ProjectUserRoleRelationship
from taskmanagement.models import Activity
from media.models import Attachment


register = template.Library()

@register.assignment_tag
def get_previous_question_value(quest,quarter,i):
    number_dict = {0:"First",1:"second",2:"Third",3:"Fourth",4:"Fifth",5:"Sixth",6:"Seventh",7:"Eigth",8:"Ninth",9:"Tenth"}
    heading_label = {''}
    text = ""
    if quest.slug == "heading":
        text = "Previous Quarter Updates"
    elif quest.slug == "sub-heading":
        text = number_dict.get(i) + " Quarter Updates" 
    elif quest.slug == "duration":
        text = quarter
    return text

@register.assignment_tag
def get_previous_subquestions(quest):
    question_list = Question.objects.filter(parent=quest).order_by("order")
    return question_list
