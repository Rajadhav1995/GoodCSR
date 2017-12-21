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
                                    ReportParameter,ReportMilestoneActivity,RemoveQuestion)
from media.models import (Comment,)
from userprofile.models import ProjectUserRoleRelationship
from taskmanagement.models import Activity,Milestone
from media.models import Attachment
from projectmanagement.views import parameter_pie_chart,get_timeline_process
from ast import literal_eval


register = template.Library()

@register.assignment_tag
def to_and(value):
    return value.replace(" ","_")

@register.assignment_tag
def get_previous_question_value(quest,quarter,i,report_obj,quarter_obj):
    number_dict = {0:"First",1:"Second",2:"Third",3:"Fourth",4:"Fifth",5:"Sixth",6:"Seventh",7:"Eigth",8:"Ninth",9:"Tenth"}
    heading_label = {'previous-quarter-update':"Previous Quarter Updates",'current-quarter-update':"Current Quarter Updates",'next-quarter-update':"Next Quarter Updates",}
    text = ""
    answer_obj = Answer.objects.get_or_none(question=quest,quarter=quarter_obj[1],content_type=ContentType.objects.get_for_model(report_obj),object_id=report_obj.id)
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
def get_milestones_activities(v,num,projectobj):
#    to get the milestone-activities for particular project based on the quarter. 
    start_date = v.split('to')[0].rstrip()
    end_date = v.split('to')[1].lstrip()
    if num == 1:
        milestone_activitieslist = Milestone.objects.filter(active=2,project=projectobj,overdue__gte = start_date,overdue__lte = end_date)
    elif num == 2:
        milestone_activitieslist = Activity.objects.filter(active=2,project=projectobj)
    return milestone_activitieslist

@register.assignment_tag
def get_milestone_name(mileobj):
#    to get the milestone name based on the activity or milestone.
    name = ''
    try:
        if mileobj.ma_type  == 1:
            obj = Milestone.objects.get_or_none(id = int (mileobj.object_id))
        elif mileobj.ma_type == 2:
            obj = Activity.objects.get_or_none(id = int (mileobj.object_id))
        if obj:
            name = obj.name
    except:
        name = mileobj.name
    return name


@register.assignment_tag
def get_parameters_list(quest,quarterreportobj):
    try:
        answerobj = Answer.objects.get(question=quest,quarter=quarterreportobj)
        answerlist = answerobj.inline_answer
        parameterlist = ReportParameter.objects.filter(id__in = eval(answerlist),active=2)
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
    milestone = Milestone.objects.filter(project = projectobj,overdue__gte=start_date,overdue__lte=end_date)
    timeline_json,timeline_json_length = get_timeline_process(timeline,milestone)
    return timeline_json,timeline_json_length

@register.assignment_tag
def get_timeline_json(projectobj,quarter_obj):
    timeline = Attachment.objects.filter(content_type = ContentType.objects.get_for_model(projectobj),object_id = projectobj.id,active=2,attachment_type= 1,date__gte = quarter_obj.start_date,date__lte = quarter_obj.end_date ).order_by('date')
    today = datetime.today()
    milestone = Milestone.objects.filter(project = projectobj,overdue__gte = quarter_obj.start_date,overdue__lte = quarter_obj.end_date)
    timeline_json,timeline_json_length = get_timeline_process(timeline,milestone)
    return timeline_json,timeline_json_length
    
@register.assignment_tag
def get_timeline_json_pdf(projectobj,quarter_obj):
    start_date = quarter_obj.split(' to ')[0].rstrip()
    end_date = quarter_obj.split(' to ')[1].rstrip()
    # import ipdb; ipdb.set_trace()
    timeline = Attachment.objects.filter(content_type = ContentType.objects.get_for_model(projectobj),object_id = projectobj.id,active=2,attachment_type= 1,date__gte = start_date,date__lte = end_date ).order_by('date')
    today = datetime.today()
    milestone = Milestone.objects.filter(project = projectobj,overdue__gte = start_date,overdue__lte = end_date)
    timeline_json,timeline_json_length = get_timeline_process(timeline,milestone)
    if timeline_json_length >5:
        time_length = 5
        if timeline_json_length/2 == 0:
            timeloop = int(timeline_json_length/5)
        else:
            timeloop = int(timeline_json_length/5)+1 
    else:
        time_length = timeline_json_length
        timeloop = 1
    return timeline_json,timeline_json_length,time_length,range(timeloop)
 
@register.assignment_tag   
def get_final_questions(quarter_question_list,block_type,object_id,period,report_id,quest_removed):
    quest_list = []
    removed_ques = []
    main_quest = []
    block_slug = {3:"previous-quarter-update",4:"current-quarter-update",5:"next-quarter-update"}
    remove_obj_id=''
    if object_id != None:
        quarter_report = QuarterReportSection.objects.get_or_none(id=object_id.id)
        quest_list = RemoveQuestion.objects.get_or_none(quarter_report__id=report_id,block_type=block_type,quarter_period=period,
        content_type=ContentType.objects.get_for_model(quarter_report),object_id = quarter_report.id)
    else:
        quest_list = RemoveQuestion.objects.get_or_none(quarter_report__id=report_id,block_type=block_type,quarter_period=period)

    if quest_list:
        if quest_removed == "false":
            remove_obj_id = quest_list.id
            final_quest_list = quarter_question_list.exclude(id__in= literal_eval(quest_list.text)).order_by('id')
        else:
            
            remove_obj_id = quest_list.id
            final_quest_list = quarter_question_list.filter(id__in=literal_eval(quest_list.text)).order_by('id')
            parent_quest = Question.objects.filter(id__in = eval(quest_list.text)).values_list('parent',flat=True)
            for parent in parent_quest:
                if parent :
                    main_quest.append(Question.objects.get_or_none(id=parent))
            if main_quest:
                final_list = list(chain(final_quest_list))
                final_list.extend(list(set(main_quest)))
                final_quest_list = final_list
    else:
        if quest_removed == 'false':
            final_quest_list = quarter_question_list
        else:
            final_quest_list = []
    return final_quest_list,remove_obj_id
    
@register.assignment_tag
def get_previous_removed(sub_questions,quest_removed,remove_id):
    final_list=[]
    main_quest = []
    try:
        quest_list = RemoveQuestion.objects.get(id=remove_id)
    except:
        quest_list = None
    if quest_list and quest_list.text != None:
        if quest_removed == 'false':
            sub_quest_list = sub_questions.exclude(id__in = eval(quest_list.text)).order_by('id')
        else:
            sub_quest_list = sub_questions.filter(id__in = eval(quest_list.text)).order_by('id')
           
    else:
        sub_quest_list = sub_questions
    return sub_quest_list
