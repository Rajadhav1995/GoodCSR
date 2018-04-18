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
import json
#create views of dashboard

@check_loggedin_access
def admin_dashboard(request):
    # this function is to show detail view of dashboard
    # 
    state_count = {}
    uu={}
    # 
    user_id = request.session.get('user_id')
    # this function is to show detail view of dashboard
    user_obj = UserProfile.objects.get(user_reference_id = user_id )
    from projectmanagement.templatetags import urs_tags
    # getting users who has permission to
    # view/edit project
    obj_list = urs_tags.userprojectlist(user_obj)
    project_count = obj_list.count()
    projectuseridlist = ProjectUserRoleRelationship.objects.filter(active=2, project__in = obj_list).values_list("user__id",flat=True)
    projectrole_id = []
    # roles
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
    project_list = obj_list.values_list('id',flat=True).order_by('id')
    location_obj = ProjectLocation.objects.filter(active=2,object_id__in=project_list)
    # this dictionary is for defining all abbrevations
    # of all states in India
    # for sending proper data in json format
    state_abbr = {'ANDAMAN & NICOBAR ISLANDS':'AN','ARUNACHAL PRADESH':'AR','ANDHRA PRADESH':'AP','DAMAN & DIU':'DD','Chattisgarh':'CT','HARYANA':'HR','MAHARASHTRA':'MH','DADRA & NAGAR HAVELI':'DN','MADHYA PRADESH':'MP','TRIPURA':'TR','RAJASTHAN':'RJ','HIMACHAL PRADESH':'RJ','GUJARAT':'GJ','MEGHALAYA':'ML','KARNATAKA':'KA','PUNJAB':'PB','ODISHA':'OR','DELHI':'DL','JHARKHAND':'JH','Chandigarh':'CH','BIHAR':'BR','WEST BENGAL':'WB','MIZORAM':'MZ','UTTARAKHAND':'UT','UTTAR PRADESH':'UP','TAMIL NADU':'TN','TELANGANA':'TG','SIKKIM':'SK','JAMMU & KASHMIR':'JK','PONDICHERRY':'PY','NAGALAND':'NL','MANIPUR':'MN','LAKSHADWEEP':'LD','KERALA':'KL','GOA':'GA','ASSAM':'AS'}
    json_data = []
    # here we are creating data for India map where 
    # logged in user will be able to see highlighted states in map
    # 
    for i in location_obj:
        if i.location.boundary_level == 3:
            data = {'name':state_abbr.get(str(i.location.parent.name)),'nap':11}
        elif i.location.boundary_level == 2:
            data = {'name':state_abbr.get(str(i.location.name)),'nap':11}
        json_data.append(data)
    # 
    json_data = [dict(tupleized) for tupleized in set(tuple(item.items()) for item in json_data)]
    json_data = json.dumps(json_data)
    paginator = Paginator(obj_list, 3)
    # 
    try:
        projectobj = paginator.page(page)
    except PageNotAnInteger:
        projectobj = paginator.page(1)
    except EmptyPage:
        projectobj = paginator.page(paginator.num_pages)
    return render(request,'corporate_dashboard.html',locals())

# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.