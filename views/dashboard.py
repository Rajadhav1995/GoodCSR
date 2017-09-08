from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Sum
from projectmanagement.models import (UserProfile,Project,ProjectFunderRelation)
from userprofile.models import (ProjectUserRoleRelationship,)
from taskmanagement.views import (updates,corp_task_completion_chart,
    total_tasks_completed,corp_total_budget,corp_total_budget_disbursed)

#create views of dashboard

def admin_dashboard(request):
    user_id = request.session.get('user_id')
    user_obj = UserProfile.objects.get(user_reference_id = user_id )
    if user_obj.is_admin_user == True:
        obj_list = Project.objects.filter(active=2)
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
    projectuserlist = ProjectUserRoleRelationship.objects.filter(project__created_by = user_obj)
    total_beneficiaries = obj_list.aggregate(Sum('no_of_beneficiaries')).values()[0]
    updates_list = updates(obj_list)
    tasks_progress = corp_task_completion_chart(obj_list)
    total_budget = corp_total_budget(obj_list)
    budget = corp_total_budget_disbursed(obj_list)
    return render(request,'corporate_dashboard.html',locals())


