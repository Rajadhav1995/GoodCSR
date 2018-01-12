from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Sum
from itertools import chain
from projectmanagement.models import (UserProfile,Project,ProjectFunderRelation)
from media.models import ProjectLocation
from userprofile.models import (ProjectUserRoleRelationship,)
from taskmanagement.views import (updates,corp_task_completion_chart,
    total_tasks_completed,corp_total_budget,corp_total_budget_disbursed)
from menu_decorators import check_loggedin_access
from pmu.settings import PMU_URL
from django.core.paginator import Paginator,Page
#create views of dashboard

@check_loggedin_access
def admin_dashboard(request):
    state_count = {}
    uu={}
    user_id = request.session.get('user_id')
    user_obj = UserProfile.objects.get(user_reference_id = user_id )
    from projectmanagement.templatetags import urs_tags
    obj_list = urs_tags.userprojectlist(user_obj)
    project_count = obj_list.count()
    projectuseridlist = ProjectUserRoleRelationship.objects.filter(active=2, project__in = obj_list).values_list("user__id",flat=True)
    projectrole_id = []
    for i in projectuseridlist:
        projectuserobj = ProjectUserRoleRelationship.objects.filter(active=2, user__id=int(i),project__in = obj_list).latest("id")
        if projectuserobj.id not in projectrole_id:
            projectrole_id.append(projectuserobj.id)
    projectuserlist = ProjectUserRoleRelationship.objects.filter(active=2, id__in = projectrole_id)
    projectuserlist = list(set(projectuserlist))
    total_beneficiaries = obj_list.aggregate(Sum('no_of_beneficiaries')).values()[0]
    updates_list = updates(obj_list)
    tasks_progress = corp_task_completion_chart(obj_list)
    total_budget = corp_total_budget(obj_list)
    budget = corp_total_budget_disbursed(obj_list)
    image = PMU_URL
    page = request.GET.get('page', 1)
    location_obj = ProjectLocation.objects.filter(active=2)
    # for i in location_obj:
        # state_count.update({str(i.location.parent.name):1})
    paginator = Paginator(obj_list, 3)
    try:
        projectobj = paginator.page(page)
    except PageNotAnInteger:
        projectobj = paginator.page(1)
    except EmptyPage:
        projectobj = paginator.page(paginator.num_pages)
    return render(request,'corporate_dashboard.html',locals())
