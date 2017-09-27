import requests,ast
import datetime
import json
from django import template
from django.db.models import Sum
from itertools import chain
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from pmu.settings import (SAMITHA_URL,PMU_URL)
from projectmanagement.models import (Project, UserProfile,ProjectFunderRelation)
from budgetmanagement.models import (Budget,ProjectBudgetPeriodConf,BudgetPeriodUnit)
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
    print projectobj
    attachment = Attachment.objects.filter(object_id=projectobj.id,content_type=ContentType.objects.get(model='project'))
    return attachment
