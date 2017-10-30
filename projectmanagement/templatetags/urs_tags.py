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
from projectmanagement.models import (Project, UserProfile,ProjectFunderRelation,ProjectParameter)
from budgetmanagement.models import (Budget,ProjectBudgetPeriodConf,BudgetPeriodUnit,
                                ReportParameter, Question,Answer,QuarterReportSection)
from media.models import (Comment,)
from userprofile.models import ProjectUserRoleRelationship
from taskmanagement.models import Activity
from media.models import Attachment



register = template.Library()

@register.assignment_tag
def get_user_permission(request):
    user_id = request.session.get('user_id')
    user_obj = UserProfile.objects.get_or_none(user_reference_id = user_id )
    return user_obj

@register.assignment_tag
def get_funder(projectobj):
    funderobj = ProjectFunderRelation.objects.get_or_none(project = projectobj)
    return funderobj

def userprojectlist(user_obj):
    if user_obj.is_admin_user == True:
        obj_list = Project.objects.filter(active=2)
    elif user_obj.owner == True and user_obj.organization_type == 1:
        project_ids = ProjectFunderRelation.objects.filter(funder = user_obj).values_list("project_id",flat=True)
        user_project_ids = ProjectUserRoleRelationship.objects.filter(user = user_obj).values_list('project_id',flat=True)
        final_project_ids = list(set(chain(project_ids, user_project_ids))) 
        obj_list = Project.objects.filter(id__in = final_project_ids,active=2)
    elif user_obj.owner == True and user_obj.organization_type == 2:
        project_ids = ProjectFunderRelation.objects.filter(implementation_partner = user_obj).values_list("project_id",flat=True)
        user_project_ids = ProjectUserRoleRelationship.objects.filter(user = user_obj).values_list('project_id',flat=True)
        final_project_ids = list(set(chain(project_ids, user_project_ids))) 
        obj_list = Project.objects.filter(id__in = final_project_ids,active=2)
    else:
        project_ids = ProjectUserRoleRelationship.objects.filter(user = user_obj).values_list("project_id",flat=True)
        obj_list = Project.objects.filter(id__in = project_ids,active=2)
    return obj_list

@register.assignment_tag
def get_user_project(request):
    user_id = request.session.get('user_id')
    user_obj = UserProfile.objects.get(user_reference_id = user_id )
    obj_list = userprojectlist(user_obj)
    project_count = obj_list.count()
    return obj_list

@register.assignment_tag
def get_budget_lineitem(row,projectobj):
    budget_periodobj = ProjectBudgetPeriodConf.objects.latest_one(project = projectobj,row_order = int(row),active=2)
    try:
        lineitem = BudgetPeriodUnit.objects.get(budget_period = budget_periodobj,active=2)
    except:
        lineitem = None
    return lineitem

@register.assignment_tag
def get_quarter_order(quarter_type,projectobj):
    quarter_order=''
    quarter_order = QuarterReportSection.objects.latest_one(project__project=projectobj,quarter_type=quarter_type)
    if quarter_order:
        quarter_order = quarter_order.quarter_order
    return quarter_order

@register.assignment_tag
def get_quarter_details(row,quarter,projectobj):
    try:
        line_itemobj = BudgetPeriodUnit.objects.get(row_order = int(row),quarter_order=int(quarter),budget_period__project=projectobj,active=2)
    except:
        line_itemobj = BudgetPeriodUnit.objects.latest_one(row_order = int(row),quarter_order=int(quarter),budget_period__project=projectobj,active=2)
    return line_itemobj

@register.assignment_tag
def get_comment(line_itemobj):
    try:
        comment = Comment.objects.get_or_none(content_type=ContentType.objects.get_for_model(line_itemobj),object_id=int(line_itemobj.id))
    except:
        comment = None
    return comment

@register.assignment_tag
def get_line_total(row,projectobj):
    budget_periodunitlist = BudgetPeriodUnit.objects.filter(budget_period__project = projectobj,active=2,row_order=row)
    total_planned_cost = budget_periodunitlist.aggregate(Sum('planned_unit_cost')).values()[0]
    total_planned_cost = int(total_planned_cost) if total_planned_cost else 0
    return total_planned_cost

@register.assignment_tag
def get_utlizedline_total(row,projectobj):
    budget_periodunitlist = BudgetPeriodUnit.objects.filter(budget_period__project = projectobj,active=2,row_order=row)
    total_utilized_cost = budget_periodunitlist.aggregate(Sum('utilized_unit_cost')).values()[0]
    total_utilized_cost = int(total_utilized_cost) if total_utilized_cost else 0
    return total_utilized_cost

@register.assignment_tag
def get_org_logo(projectobj):
    funderobj = get_funder(projectobj)
    data = {'company_name':str(funderobj.funder.organization) if funderobj else ''}
    ''' calling function to return the company logo based on the project'''
    companyobj = requests.post(SAMITHA_URL + '/pmu/company/logo/', data=data)
    validation_data = json.loads(companyobj.content)
    front_image = validation_data.get('organization_logo')
    org_logo = validation_data.get('front_image')
    return org_logo

@register.assignment_tag
def get_activities(projectobj):
    activity = Activity.objects.filter(project=projectobj,active=2)
    return activity

@register.assignment_tag
def get_attachments(projectobj):
    attachment = Attachment.objects.filter(object_id=projectobj.id,content_type=ContentType.objects.get(model='project'))
    return attachment


def diff_month(d1, d2):
    duration = (d1.year - d2.year) * 12 + d1.month - d2.month
    if d2.day < 15:
        duration = duration + 1
    return duration

@register.assignment_tag
def get_duration_month(date):
    duration = 0
    try:
        start_date = date.split('to')[0].rstrip()
        end_date = date.split('to')[1].lstrip()
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        duration = diff_month(end_date,start_date)
    except:
        pass
    return duration

@register.assignment_tag
def get_parameter(obj,block_id):
    question_obj = Question.objects.get_or_none(slug='parameter-section',block=block_id)
    answer_obj = Answer.objects.get_or_none(quarter=obj.id,question=question_obj)
    main_list =[]
    master_list = []
    master_names = []
    if answer_obj:
        parameter_obj = ProjectParameter.objects.filter(id__in=eval(answer_obj.inline_answer))
        from projectmanagement.views import parameter_pie_chart,pie_chart_mainlist_report
        for i in parameter_obj:
            main_list = pie_chart_mainlist_report(i,obj.start_date,obj.end_date)
            master_list.append(main_list)
            master_names.append(i.name)
    return master_list,master_names

@register.filter
def get_at_index(list, index):
    return list[index]

@register.assignment_tag
def get_budget_detail(block,quarter,obj):
    question_obj = Question.objects.get_or_none(slug='about-the-budget',block=block)
    answer_obj = Answer.objects.get_or_none(quarter=quarter,object_id=obj.id)

@register.assignment_tag
def get_about_parameter(quarter,obj):
    # template tag to get parameter detail quarter wise in report detail page
    about_parameter = ''
    question_obj = Question.objects.get_or_none(slug='about-parameter')
    answer_obj = Answer.objects.get_or_none(quarter=quarter,object_id=obj.id,question=question_obj)
    if answer_obj:
        about_parameter = answer_obj.text
    return about_parameter

@register.assignment_tag
def get_about_quarter(quarter,obj,block):
    # this template tag we are using to get quarter details in report detai page
    answer_obj = ''
    question = Question.objects.get_or_none(slug='about-the-quarter',block=block)
    answer_obj = Answer.objects.get_or_none(question=question,object_id=obj.id,quarter=quarter)
    if answer_obj:
        about_quarter = answer_obj.text
    return about_quarter

@register.assignment_tag
def get_report_list(obj):
    # this template tag we are using to list report which have answer
    answer_obj = Answer.objects.filter(object_id=obj.id,content_type=ContentType.objects.get(model='projectreport'))
    if answer_obj:
        report_list = 1
    else:
        report_list = 0
    return report_list