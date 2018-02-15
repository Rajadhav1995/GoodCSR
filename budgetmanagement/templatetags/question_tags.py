import requests,ast
import datetime
import json
from django import template
from django.db.models import Sum
from datetime import datetime, timedelta
from dateutil import relativedelta
from itertools import chain
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from pmu.settings import (SAMITHA_URL,PMU_URL)
from projectmanagement.models import (Project, UserProfile,ProjectFunderRelation)
from budgetmanagement.models import (Budget,ProjectBudgetPeriodConf,QuarterReportSection,
                                    BudgetPeriodUnit,Question,Block,Answer,
                                    ReportParameter,ReportMilestoneActivity,RemoveQuestion,
                                    ProjectReport)
from media.models import (Comment,)
from userprofile.models import ProjectUserRoleRelationship
from taskmanagement.models import Activity,Milestone
from media.models import Attachment
from projectmanagement.views import parameter_pie_chart,get_timeline_process
from ast import literal_eval
from budgetmanagement.manage_budget import get_budget_quarters
from collections import OrderedDict

register = template.Library()
#According to Wikipedia the exact definition of a goal is:
# A desired result a person or a system envisions, plans and commits to achieve a personal or organizational desired end-point in some sort of assumed development. Many people endeavor to reach goals within a finite time by setting deadlines. 
#In other words, any planning you do for the future regardless of what it is, is a goal. 
#So the next time you are planning on doing the weekly chores or decide on watching that really cool action movie after work, always keep in mind that these small tasks account as goals and while seemingly insignificant you are goal setting.
# Just like how sunlight can't burn through anything without a magnifying glass focusing it, 
#you can't achieve anything unless a goal is focusing your effort. 
#Because at the end of the day goals are what give you direction in life. 
#By setting goals for yourself you give yourself a target to shoot for. 
#This sense of direction is what allows your mind to focus on a target and rather than waste energy shooting aimlessly,
# allows you to hit your target and reach your goal. 
#By setting goals for yourself you are able to measure your progress because you always have a fixed endpoint or benchmark to compare with. Take this scenario for example: David makes a goal to write a book with a minimum of 300 pages. He starts writing every day and works really hard but along the way, he loses track of how many more pages he has written and how much more he needs to write. 
#So rather than panicking David simply counts the number of pages he has already written and he instantly determines his progress and knows how much further he needs to go.
@register.assignment_tag
def to_and(value):
    return value.replace(" ","_")

@register.assignment_tag
def get_previous_question_value(quest,quarter,i,report_obj,quarter_obj):
    number_dict = {0:"First",1:"Second",2:"Third",3:"Fourth",4:"Fifth",5:"Sixth",6:"Seventh",7:"Eigth",8:"Ninth",9:"Tenth"}
    heading_label = {'previous-quarter-update':"Previous Quarter Updates",'current-quarter-update':"Current Quarter Updates",'next-quarter-update':"Next Quarter Updates",}
    month_label = {'previous-quarter-update':"Previous Month Updates",'current-quarter-update':"Current Month Updates",'next-quarter-update':"Next Month Updates",}
    text = ""
    answer_obj = Answer.objects.get_or_none(question=quest,quarter=quarter_obj[1],content_type=ContentType.objects.get_for_model(report_obj),object_id=report_obj.id)
    if answer_obj:
        text = answer_obj.text 
    else:
        if quest.slug == "heading":
            text = heading_label.get(quest.block.slug) if report_obj.report_type == 1 else month_label.get(quest.block.slug)
        elif quest.slug == "sub-heading":
            extra_text = " Quarter Updates" if report_obj.report_type == 1 else " Month Updates"
            text = number_dict.get(i) + extra_text 
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
            name = obj.name if obj.name else ''
        else:
            name = mileobj.name
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

def get_removed_quest_list(quest_removed,quest_list,quarter_question_list):
#    splitted the below function
    remove_obj_id=''
    main_quest = []
    if quest_removed == "false":
        remove_obj_id = quest_list.id
        final_quest_list = quarter_question_list.exclude(id__in= literal_eval(quest_list.text)).order_by('id') if quest_list.text != '[]' else ''
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
    return final_quest_list,remove_obj_id


@register.assignment_tag   
def get_final_questions(quarter_question_list,block_type,object_id,period,report_id,quest_removed):
    quest_list = []
    removed_ques = []
    main_quest = []
    block_slug = {3:"previous-quarter-update",4:"current-quarter-update",5:"next-quarter-update"}
    remove_obj_id=''
    if object_id != None :
        quarter_report = QuarterReportSection.objects.get_or_none(id=object_id.id)
        quest_list = RemoveQuestion.objects.get_or_none(quarter_report__id=report_id,block_type=block_type,quarter_period=period,
        content_type=ContentType.objects.get_for_model(quarter_report),object_id = quarter_report.id)
    else:
        quest_list = RemoveQuestion.objects.get_or_none(quarter_report__id=report_id,block_type=block_type,quarter_period=period)
    
    if quest_list and quest_list.text and quest_list.text != '[]' :

#        calling the function to reduce the complexity: meghana
        final_quest_list,remove_obj_id = get_removed_quest_list(quest_removed,quest_list,quarter_question_list)
    else:
        final_quest_list = []
        if quest_removed == 'false':
            final_quest_list = quarter_question_list
    final_quest_list = get_sorted_list(final_quest_list)
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
    
@register.assignment_tag
def get_previous_tab_quests(block_id):
    block_slug = {1:"cover-page",2:"project-summary-sheet",3:"previous-quarter-update",4:"current-quarter-update",5:"next-quarter-update"}
    block = int(block_id)
    ques_ids_list =Question.objects.filter(active=2,block__slug=block_slug.get(block)).values_list('id',flat=True).order_by('id')
    return map(int,(list(chain(ques_ids_list))))
    
@register.assignment_tag
def get_quarter_tab_removed(ques_list,period,block_type,object_id,report_obj):
    tab_removed = ''
    removed_list = []
    if object_id != 'None' and str(object_id) != '' and object_id != None:
        quarter_report = QuarterReportSection.objects.get_or_none(id=object_id.id)
        remove_obj = RemoveQuestion.objects.get_or_none(active=2,quarter_report= report_obj,
                block_type = block_type,quarter_period = period,
                content_type = ContentType.objects.get_for_model(quarter_report),
                object_id = quarter_report.id)
    else:
        remove_obj = RemoveQuestion.objects.get_or_none(quarter_report= report_obj,
                block_type = int(block_type),quarter_period = str(period))
    if remove_obj and remove_obj.text :
        removed_list = literal_eval(remove_obj.text)
        remove_id = remove_obj.id if str(remove_obj.text) != '[]' else ''
        if set(removed_list) == set(ques_list):
            tab_removed = 'true'
        else:
            tab_removed = 'false'
    else:
        tab_removed = 'false'
        remove_id = ''
    return tab_removed,remove_id


def get_sorted_list(final_quest_list):
    ids_list = []
    for i in final_quest_list:
        ids_list.append(i.id)
    final_list = Question.objects.filter(id__in=list(set(ids_list))).order_by('id')
    return final_list

@register.assignment_tag
def get_budget_period(projectobj,budgetobj,v):
    from datetime import datetime
    start_date = v.split('to')[0].rstrip()
    end_date = v.split('to')[1].lstrip()
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    budget_period = ProjectBudgetPeriodConf.objects.filter(project = projectobj,budget = budgetobj,active=2,start_date = start_date,end_date = end_date).values_list('row_order', flat=True).distinct()
    return budget_period

@register.assignment_tag
def get_month_budget_period(projectobj,budgetobj,v):
    from datetime import datetime
    budget_period = ProjectBudgetPeriodConf.objects.filter(project = projectobj,budget = budgetobj,active=2).values_list('row_order', flat=True).distinct()
    return budget_period
    
@register.assignment_tag
def get_row_details(row,quarter,projectobj):
    # this template tag is used to get budget lineitems details
    try:
        line_itemobj = BudgetPeriodUnit.objects.get(row_order = int(row),quarter_order=int(quarter),budget_period__project=projectobj,active=2)
    except:
        line_itemobj = BudgetPeriodUnit.objects.latest_one(row_order = int(row),quarter_order=int(quarter),budget_period__project=projectobj,active=2)
    return line_itemobj

@register.assignment_tag
def show_budget_table(date,block_id,report_obj):
    if report_obj.report_type == 2:
        budget_table = False
        date_list = []
        month = int(date.split(' to ')[0].split('-')[1])
        budgetobj = Budget.objects.get(project = report_obj.project,active=2)
        quarter_list = get_budget_quarters(budgetobj)
        start_q = quarter_list.get(0)
        end_q = quarter_list.get(quarter_list.keys()[-1])
        date_list.append(start_q.split(' to ')[0])
        date_list.append(end_q.split(' to ')[1])
        start, end = [datetime.strptime(_, "%Y-%m-%d") for _ in date_list]
        month_list = OrderedDict(((start + timedelta(_)).strftime(r"%-m"), None) for _ in xrange((end - start).days)).keys()
        month_list = map(int,month_list)
        first_month = month_list[0::3]
        second_month = month_list[1::3]
        third_month = month_list[2::3]
        if (block_id == 3 and month in third_month) or (block_id == 4) or (block_id == 5 and month in first_month):
            budget_table = True
    else:
        budget_table = True
    return budget_table
