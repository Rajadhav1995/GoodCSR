from django import template
from django.contrib.auth.models import User
from projectmanagement.models import (Project, UserProfile)
from budgetmanagement.models import (Budget,ProjectBudgetPeriodConf,BudgetPeriodUnit)

register = template.Library()

@register.assignment_tag
def get_user_project(request):
    user_id = request.session.get('user_id')
    user_obj = UserProfile.objects.get(user_reference_id = user_id )
    obj_list = Project.objects.filter(created_by = user_obj)
    project_count = obj_list.count()
    return obj_list

@register.assignment_tag
def get_budget_lineitem(row):
#    import ipdb;ipdb.set_trace();
    budget_periodobj = ProjectBudgetPeriodConf.objects.filter(row_order = int(row))[0]
    try:
        lineitem = BudgetPeriodUnit.objects.get(budget_period = budget_periodobj)
    except:
        lineitem = None
    return lineitem

@register.assignment_tag
def get_quarter_details(row,quarter):
    try:
        line_itemobj = BudgetPeriodUnit.objects.get_or_none(row_order = int(row),quarter_order=int(quarter))
    except:
        line_itemobj = BudgetPeriodUnit.objects.latest_one(row_order = int(row),quarter_order=int(quarter))
    return line_itemobj
