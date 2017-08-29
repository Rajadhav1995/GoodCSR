from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Sum
from projectmanagement.models import (UserProfile,Project)
from userprofile.models import (ProjectUserRoleRelationship,)
from taskmanagement.views import (updates,corp_task_completion_chart)

#create views of dashboard

def admin_dashboard(request):
    user_id = request.session.get('user_id')
    user_obj = UserProfile.objects.get(user_reference_id = user_id )
    obj_list = Project.objects.filter(created_by = user_obj)
    project_count = obj_list.count()
    projectuserlist = ProjectUserRoleRelationship.objects.filter(project__created_by = user_obj)
    total_beneficiaries = obj_list.aggregate(Sum('no_of_beneficiaries')).values()[0]
    updates_list = updates(obj_list)
    tasks_progress = corp_task_completion_chart(obj_list)
    return render(request,'corporate_dashboard.html',locals())

