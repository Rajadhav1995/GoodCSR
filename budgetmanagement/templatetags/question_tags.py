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
from budgetmanagement.models import (Budget,ProjectBudgetPeriodConf,QuarterReportSection,
                                    BudgetPeriodUnit,Question,Block,Answer,
                                    ReportParameter,ReportMilestoneActivity)
from media.models import (Comment,)
from userprofile.models import ProjectUserRoleRelationship
from taskmanagement.models import Activity,Milestone
from media.models import Attachment
from projectmanagement.views import parameter_pie_chart,get_timeline_process


register = template.Library()

@register.assignment_tag
def to_and(value):
    return value.replace(" ","_")

@register.assignment_tag
def get_previous_question_value(quest,quarter,i,report_obj):
    number_dict = {0:"First",1:"second",2:"Third",3:"Fourth",4:"Fifth",5:"Sixth",6:"Seventh",7:"Eigth",8:"Ninth",9:"Tenth"}
    heading_label = {'previous-quarter-update':"Previous Quarter Updates",'current-quarter-update':"Current Quarter Updates",'next-quarter-update':"Next Quarter Updates",}
    text = ""
    answer_obj = Answer.objects.get_or_none(question=quest,content_type=ContentType.objects.get_for_model(report_obj),object_id=report_obj.id)
    if answer_obj:
        text = answer_obj.text 
    else:
        if quest.slug == "heading":
            text = heading_label.get(quest.block.slug)
        elif quest.slug == "sub-heading":
            text = number_dict.get(i) + " Quarter Updates" 
        elif quest.slug == "duration":
            text = quarter
    return text

@register.assignment_tag
def get_previous_subquestions(quest):
    question_list = Question.objects.filter(parent=quest).order_by("order")
    return question_list

@register.assignment_tag
def getreport_status(report_id,v,num):
    start_date = v.split('to')[0].rstrip()
    end_date = v.split('to')[1].lstrip()
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    quarterreportobj = QuarterReportSection.objects.get_or_none(project__id=int(report_id),quarter_type=num,start_date=start_date,end_date=end_date)
    if quarterreportobj:
        status = True
    else:
        status = False
    return status,quarterreportobj

@register.assignment_tag
def get_answer_question(quest,quarterreportobj):
    try:
        answerobj = Answer.objects.get(question = quest,quarter=quarterreportobj)
        text = answerobj.text
    except:
        text = ""
    return text

@register.assignment_tag
def get_parameters_list(quest,quarterreportobj):
    try:
        answerobj = Answer.objects.get(question=quest,quarter=quarterreportobj)
        answerlist = answerobj.inline_answer
        parameterlist = ReportParameter.objects.filter(id__in = eval(answerlist))
    except:
        parameterlist = []
    return parameterlist

@register.assignment_tag
def get_milestone_list(quest,quarterreportobj):
    try:
        answerobj = Answer.objects.get(question=quest,quarter=quarterreportobj)
        answerlist = answerobj.inline_answer
        act_mile_list = ReportMilestoneActivity.objects.filter(id__in = eval(answerlist))
    except:
        act_mile_list = []
    return act_mile_list

@register.assignment_tag
def get_mile_act_images(mileobj):
    try:
        imagelist = Attachment.objects.filter(content_type = ContentType.objects.get_for_model(mileobj),object_id = mileobj.id)
    except:
        imagelist = []
    return imagelist

@register.assignment_tag
def get_timeline_progress(projectobj,v):
    start_date = v.split('to')[0].rstrip()
    end_date = v.split('to')[1].lstrip()
    start_date = datetime.strptime(start_date[:19], '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date[:19], '%Y-%m-%d').date()
    timeline = Attachment.objects.filter(content_type = ContentType.objects.get_for_model(projectobj),object_id = projectobj.id,active=2,attachment_type= 1,date__gte = start_date,date__lte = end_date ).order_by('date')
    today = datetime.today()
    milestone = Milestone.objects.filter(project = projectobj,overdue__lte=today.now())
    timeline_json,timeline_json_length = get_timeline_process(timeline,milestone)
    return timeline_json,timeline_json_length

@register.assignment_tag
def get_timeline_json(projectobj,quarter_obj):
    timeline = Attachment.objects.filter(content_type = ContentType.objects.get_for_model(projectobj),object_id = projectobj.id,active=2,attachment_type= 1,date__gte = quarter_obj.start_date,date__lte = quarter_obj.end_date ).order_by('date')
    today = datetime.today()
    milestone = Milestone.objects.filter(project = projectobj,overdue__gte = quarter_obj.start_date,overdue__lte = quarter_obj.end_date)
    timeline_json,timeline_json_length = get_timeline_process(timeline,milestone)
    return timeline_json,timeline_json_length
