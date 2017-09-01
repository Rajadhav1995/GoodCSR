from django import template
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from projectmanagement.models import (Project, UserProfile,ProjectFunderRelation)
from budgetmanagement.models import (Budget,ProjectBudgetPeriodConf,BudgetPeriodUnit)
from media.models import (Comment,)
from userprofile.models import ProjectUserRoleRelationship

register = template.Library()

@register.assignment_tag
def get_user_permission(request):
    user_id = request.session.get('user_id')
    user_obj = UserProfile.objects.get_or_none(user_reference_id = user_id )
    return user_obj


@register.assignment_tag
def get_user_project(request):
    user_id = request.session.get('user_id')
    user_obj = UserProfile.objects.get(user_reference_id = user_id )
    if user_obj.is_admin_user == True:
        obj_list = Project.objects.filter()
    elif user_obj.owner == True and user_obj.organization_type == 1:
        project_ids = ProjectFunderRelation.objects.filter(funder = user_obj).values_list("project_id",flat=True)
        obj_list = Project.objects.filter(id__in = project_ids,active=2)
    elif user_obj.owner == True and user_obj.organization_type == 2:
        project_ids = ProjectFunderRelation.objects.filter(implementation_partner = user_obj).values_list("project_id",flat=True)
        obj_list = Project.objects.filter(id__in = project_ids,active=2)
    else:
        project_ids = ProjectUserRoleRelationship.objects.filter(user = user_obj).values_list("project_id",flat=True)
        obj_list = Project.objects.filter(id__in = project_ids,active=2)
    project_count = obj_list.count()
    return obj_list

@register.assignment_tag
def get_budget_lineitem(row,projectobj):
#    import ipdb;ipdb.set_trace();
    budget_periodobj = ProjectBudgetPeriodConf.objects.latest_one(project = projectobj,row_order = int(row),active=2)
    try:
        lineitem = BudgetPeriodUnit.objects.get(budget_period = budget_periodobj)
    except:
        lineitem = None
    return lineitem

@register.assignment_tag
def get_quarter_details(row,quarter,projectobj):
    try:
        line_itemobj = BudgetPeriodUnit.objects.get_or_none(row_order = int(row),quarter_order=int(quarter),budget_period__project=projectobj,active=2)
    except:
        line_itemobj = BudgetPeriodUnit.objects.latest_one(row_order = int(row),quarter_order=int(quarter),budget_period__project=projectobj,active=2)
    return line_itemobj

@register.assignment_tag
def get_comment(line_itemobj):
    comment = Comment.objects.get_or_none(content_type=ContentType.objects.get_for_model(line_itemobj),object_id=int(line_itemobj.id))
    return comment

