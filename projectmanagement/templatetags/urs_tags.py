import requests,ast
import datetime
import json
import os
from django.core.files import File 
from pmu.settings import BASE_DIR
from django import template
from django.db.models import Sum
from datetime import datetime
from dateutil import relativedelta
from itertools import chain
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from pmu.settings import (SAMITHA_URL,PMU_URL)
from projectmanagement.models import (Project, UserProfile,ProjectFunderRelation,ProjectParameter,
                                        ProjectParameterValue)
from budgetmanagement.models import (Budget,ProjectBudgetPeriodConf,BudgetPeriodUnit,
                                ReportParameter, Question,Answer,QuarterReportSection)
from media.models import (Comment,)
from userprofile.models import ProjectUserRoleRelationship
from taskmanagement.models import Activity
from media.models import (Attachment,ScreenshotMedia)




register = template.Library()

@register.assignment_tag
def get_user_permission(request):
    # this template tag is used to get user permission
    user_id = request.session.get('user_id')
    user_obj = UserProfile.objects.get_or_none(user_reference_id = user_id )
    return user_obj

@register.assignment_tag
def get_user_permission_pmo(request):

    # this template tag is used to get user permission

    user_id = request.session.get('user_id')
    user_obj = UserProfile.objects.get_or_none(user_reference_id = user_id )
    project = Project.objects.get_or_none(slug=request.GET.get('slug'))
    pmo_user = ProjectUserRoleRelationship.objects.get_or_none(project=project,role=3,user__id=user_id)
    admin_user = user_obj.is_admin_user
    if admin_user == True or pmo_user != '':
        option = 1
    else:
        option = 0
    return option

@register.assignment_tag
def get_funder(projectobj):
    # this template tag is used to get funder relation
    funderobj = ProjectFunderRelation.objects.get_or_none(project = projectobj)
    return funderobj

def userprojectlist(user_obj):
    # this template tag is used to get project list as per user
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
    # this template tag is used to get project list as per user
    user_id = request.session.get('user_id')
    user_obj = UserProfile.objects.get(user_reference_id = user_id )
    obj_list = userprojectlist(user_obj)
    project_count = obj_list.count()
    return obj_list

@register.assignment_tag
def get_budget_lineitem(row,projectobj):
    # this template tag is used to get budget lineitem
    budget_periodobj = ProjectBudgetPeriodConf.objects.latest_one(project = projectobj,row_order = int(row),active=2)
    try:
        lineitem = BudgetPeriodUnit.objects.get(budget_period = budget_periodobj,active=2)
    except:
        lineitem = None
    return lineitem

@register.assignment_tag
def get_quarter_order(quarter_type,projectobj):
    # this template tag is used to get quarer order
    quarter_order=''
    quarter_order = QuarterReportSection.objects.latest_one(project__project=projectobj,quarter_type=quarter_type)
    if quarter_order:
        quarter_order = quarter_order.quarter_order
    return quarter_order

@register.assignment_tag
def get_quarter_details(row,quarter,projectobj):
    # this template tag is used to get budget lineitems details
    try:
        line_itemobj = BudgetPeriodUnit.objects.get(row_order = int(row),quarter_order=int(quarter),budget_period__project=projectobj,active=2)
    except:
        line_itemobj = BudgetPeriodUnit.objects.latest_one(row_order = int(row),quarter_order=int(quarter),budget_period__project=projectobj,active=2)
    return line_itemobj

@register.assignment_tag
def get_month_quarter_details(row,v,quarter,projectobj):
    # this template tag is used to get budget lineitems details
    from datetime import datetime
    start_date = v.split('to')[0].rstrip()
    end_date = v.split('to')[1].lstrip()
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    budget_periodobj = ProjectBudgetPeriodConf.objects.get_or_none(project = projectobj,row_order = int(row),active=2,start_date__lte = start_date,end_date__gte = end_date)
    
    try:
        line_itemobj = BudgetPeriodUnit.objects.get(row_order = int(row),budget_period__project=projectobj,active=2,budget_period=budget_periodobj)
    except:
        line_itemobj = BudgetPeriodUnit.objects.latest_one(row_order = int(row),budget_period__project=projectobj,active=2,budget_period=budget_periodobj)
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
    # this template tag is used to get line total in budget detail table
    budget_periodunitlist = BudgetPeriodUnit.objects.filter(budget_period__project = projectobj,active=2,row_order=row)
    total_planned_cost = budget_periodunitlist.aggregate(Sum('planned_unit_cost')).values()[0]
    total_planned_cost = int(total_planned_cost) if total_planned_cost else 0
    return total_planned_cost

@register.assignment_tag
def get_utlizedline_total(row,projectobj):
    # this template tag is used to get utilized total amount in budget detail page
    budget_periodunitlist = BudgetPeriodUnit.objects.filter(budget_period__project = projectobj,active=2,row_order=row)
    total_utilized_cost = budget_periodunitlist.aggregate(Sum('utilized_unit_cost')).values()[0]
    total_utilized_cost = int(total_utilized_cost) if total_utilized_cost else 0
    return total_utilized_cost

@register.assignment_tag
def get_org_logo(projectobj):
    # this template tag is used to get ogrganozation logo
    funderobj = get_funder(projectobj)
    data = {'company_name':str(funderobj.funder.organization) if funderobj else '',
            'ngo_name':str(funderobj.implementation_partner.organization if funderobj else '')}
    ''' calling function to return the company logo based on the project'''
    companyobj = requests.post(SAMITHA_URL + '/pmu/company/logo/', data=data)
    validation_data = json.loads(companyobj.content)
    front_image = validation_data.get('organization_logo')
    org_logo = validation_data.get('front_image')
    ngo_logo = validation_data.get('ngo_image')
    return org_logo,ngo_logo

@register.assignment_tag
def get_activities(projectobj):
    # this template tag is used to get activities of project
    #NOT USING THIS TAG
    activity = Activity.objects.filter(project=projectobj,active=2)
    return activity

@register.assignment_tag
def get_attachments(projectobj):
    # this template tag is used to get attachments for project detail popup
    attachment = Attachment.objects.filter(object_id=projectobj.id,content_type=ContentType.objects.get(model='project'))
    return attachment


def diff_month(d1, d2):
    # this template tag is used to get difference between two dates d1 and d2
    duration = (d1.year - d2.year) * 12 + d1.month - d2.month
    if d2.day < 15:
        duration = duration + 1
    return duration

@register.assignment_tag
def get_duration_month(date):
    # this template tag is used to get duration by date range
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
    # this template tag is used to get json data for parameter pie chart 
    question_obj = Question.objects.get_or_none(slug='parameter-section',block__order=block_id)
    answer_obj = Answer.objects.get_or_none(quarter=obj.id,question=question_obj)
    main_list =[]
    master_list = []
    master_names = []
    pie_chart = ''
    single_parameter = 0
    report_para = []
    if answer_obj:
        report_para = ReportParameter.objects.filter(id__in=eval(answer_obj.inline_answer))
        from projectmanagement.views import parameter_pie_chart,pie_chart_mainlist_report
        for i in report_para:
            if i.keyparameter:
                main_list = pie_chart_mainlist_report(i.keyparameter,obj.start_date,obj.end_date)
                master_list.append(main_list)
                master_names.append(i.keyparameter.name)
                if i.keyparameter.parameter_type == 'NUM' or i.keyparameter.parameter_type == 'CUR':
                    pie_chart = 0
                else:
                    pie_chart = 1
    return report_para

@register.assignment_tag
def get_parameter_values(obj,para_obj):

    # this template tag is used to get json data for parameter pie chart 
    main_list =[]
    master_list = []
    master_names = []
    parameter_type = ''
    numeric_parameter_value = 0
    report_para = []

    from projectmanagement.views import parameter_pie_chart,pie_chart_mainlist_report
    if para_obj.keyparameter:
        main_list = pie_chart_mainlist_report(para_obj.keyparameter,obj.start_date,obj.end_date)
        master_list.append(main_list)
        master_names.append(para_obj.keyparameter.name)
        if para_obj.keyparameter.parameter_type == 'NUM' or para_obj.keyparameter.parameter_type == 'CUR':
            parameter_type = 0
            numeric_parameter = ProjectParameterValue.objects.filter(keyparameter=para_obj.keyparameter,start_date__gte=obj.start_date,end_date__lte=obj.end_date).values_list('parameter_value',flat=True)
            numeric_parameter_value = sum([int(i) for i in numeric_parameter])

        else:
            parameter_type = 1
    return master_list,master_names,parameter_type,numeric_parameter_value

@register.filter
def get_at_index(list, index):
    # this template tag is used to get index value of pie chart data 
    return list[index]

import locale
import re
@register.filter
def currency(value):
    # this template tag is to convert number into currency format 
    if value == '':
        value = 0
    loc = locale.setlocale(locale.LC_MONETARY, 'en_IN')
    value = float('{:.2f}'.format(float(value)))
    if value <= 99999.99:
        value = re.sub(u'\u20b9', ' ', locale.currency(value, grouping=True).decode('utf-8')).strip()
        return re.sub(r'\.00', '', value)
    elif value >= 100000.99 and value <= 9999999.99:
        value = re.sub(u'\u20b9', ' ', locale.currency(value / 100000, grouping=True).decode('utf-8')).strip()
        return str(float(value)) + ' ' + 'Lac'
    else:
        h = locale.format("%d", value)
        value = float(h) * (0.0001 / 1000)
        value = '{:.2f}'.format(value)
        return str(float(value)) + ' ' + 'Cr'

@register.assignment_tag
def get_budget_detail(block,quarter):
    # this template tag is used to get budget detail on report detail page
    budget_detail = ''
    question_obj = Question.objects.get_or_none(slug='about-the-budget',block__order=block)
    answer_obj = Answer.objects.get_or_none(quarter=quarter,question=question_obj)
    if answer_obj:
        budget_detail = answer_obj.text
    return budget_detail

@register.assignment_tag
def get_about_parameter(quarter,obj,block):
    # template tag to get parameter detail quarter wise in report detail page
    about_parameter = ''
    question_obj = Question.objects.get_or_none(slug='parameter-section',block__order=block)
    answer_obj = Answer.objects.get_or_none(quarter=quarter,object_id=obj.id,question=question_obj)
    report_para = ReportParameter.objects.filter(id__in=eval(answer_obj.inline_answer))
    for i in report_para:
        detil = i.description
    return detil

@register.assignment_tag
def get_about_quarter(quarter,obj,block):
    # this template tag we are using to get quarter details in report detai page
    answer_obj = ''
    about_quarter = ''
    question = Question.objects.get_or_none(slug='about-the-quarter',block__order=block)
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

@register.assignment_tag
def get_risk_mitigation(obj):    
    #this template tag is used to get risk nd mitigation 
    risk_mitigation = ''
    question = Question.objects.get_or_none(slug='risks-mitigation')
    answer = Answer.objects.get_or_none(question=question,quarter=obj)
    if answer:
        risk_mitigation = answer.text
    return risk_mitigation

import datetime
@register.assignment_tag
def get_date_range(obj):
    # get date range from quarter range
    quarter = QuarterReportSection.objects.get(id=obj.id)
    duration = ''
    if quarter:
        duration = quarter.start_date.strftime('%d %b %Y')+ ' to ' + quarter.end_date.strftime('%d %b %Y')
        quarter_duration = quarter.start_date.strftime('%Y-%m-%d')+ 'to' + quarter.end_date.strftime('%Y-%m-%d')
    return duration,quarter_duration

@register.assignment_tag
def get_quarter_sections(obj):
    # get quarter sections
    quarter_section = QuarterReportSection.objects.filter(quarter_type=1,project=obj.project).order_by('quarter_order')
    return quarter_section

@register.assignment_tag
def get_next_quarter_sections(obj):
    #  get next quarter sections
    quarter_section = QuarterReportSection.objects.filter(quarter_type=3,project=obj.project).order_by('quarter_order')
    return quarter_section

import locale
@register.filter
def get_currency(amount):
    # get amount in form of currency
    locale.setlocale( locale.LC_ALL, 'en_IN.UTF-8' )
    group_amount = 0
    if amount:
        group_amount = locale.currency( float(amount), grouping=True )
        group_amount = group_amount[4:]
        amount_type = group_amount[-2:]
        if int(amount_type) == 0:
            group_amount = group_amount[:-3]
        else:
            group_amount = group_amount
    return group_amount

@register.filter
def get_ordinal_number(number):
    #  this filter will return ordinal number
    ordinal = {1:"First",2:"Second",3:"Third",4:"Fourth",5:"Fifth"}
    # this template tag is used to get text ordinal (eg if we pass '1' then we will get 'First')
    return ordinal.get(int(number))

@register.assignment_tag
def get_page_number(page_number):
    # this template tag is to increment page number for repor view
    page_obj = Answer.objects.get(text__iexact='page_count')
    page_number = page_obj.object_id
    page_obj.object_id = page_number + 1
    page_obj.save()
    return page_number

@register.assignment_tag
def get_last_page_number(page_number):
    # this template tag is to reset page number counter
    page_obj = Answer.objects.get(text__iexact='page_count')
    page_number = page_obj.object_id
    page_obj.object_id = 1
    page_obj.save()
    return page_number


@register.assignment_tag
def get_index_page_number(quarter):
    # this template tag is to rerurn index page number
    lista = [4]
    prev = len(quarter.get('Previous Quarter Updates'))
    cur = len(quarter.get('Current Quarter Updates'))
    next = len(quarter.get('Next Quarter Updates'))
    page_obj = Answer.objects.get(text__iexact='index_count')

    for i in range(prev):
        page = page_obj.object_id + 2
        lista.append(page)
        page_obj.object_id = page
        page_obj.save()
    for j in range(cur):
        page = page_obj.object_id + 3
        lista.append(page)
        page_obj.object_id = page
        page_obj.save()
    for j in range(next):
        page = page_obj.object_id + 1
        lista.append(page)
        page_obj.object_id = page
        page_obj.save()
    lista.append(13)
    page_obj = Answer.objects.get(text__iexact='index_count')
    page_number = page_obj.object_id
    page_obj.object_id = 1
    function_count = int(page_obj.inline_answer)
    page_obj.inline_answer = function_count

    page_obj.save()

    return lista[function_count]

@register.filter
def location_split(value, sep = "."):
    # this filter is to separate location
    parts = value.split(sep)
    return (parts[0], sep.join(parts[1:]))

@register.assignment_tag
def is_ceo_user(request):
    # this function is to check user is ceo or not
    user_id = request.session.get('user_id')
    user_obj = UserProfile.objects.get_or_none(user_reference_id = int(user_id ))
    ceo_user = ProjectUserRoleRelationship.objects.filter(user = user_obj,role__code = 5)
    admin_user = user_obj.is_admin_user
    if ceo_user:
        status = 0
    else:
        status = 1
    return status

@register.assignment_tag
def report_duration(date_string):
    #  get report duration
    start_date = date_string.split(' TO ')[0].rstrip()
    end_date = date_string.split(' TO ')[1].rstrip()
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    report_duration = (start_date.year - end_date.year) * 12 + start_date.month - end_date.month
    return abs(report_duration)

from budgetmanagement.manage_budget import tanchesamountlist
@register.assignment_tag
def get_tranches(duration,objects):
    # get tranches
    start_date = duration.split(' to ')[0].rstrip()
    end_date = duration.split(' to ')[1].rstrip()
    tranche_obj = objects.filter(due_date__gte=start_date,due_date__lte=end_date)
    tranche_amount = tanchesamountlist(tranche_obj)
    return tranche_obj,tranche_amount

@register.assignment_tag
def get_funder_mapping(projectobj):
    mapping = ProjectFunderRelation.objects.get_or_none(project=projectobj)
    return mapping

@register.filter
def remove_spcl_char(string):
    # this filter is to remove all special chars from string
    #  we are using this to give class name or id
    return ''.join(e for e in string if e.isalnum())