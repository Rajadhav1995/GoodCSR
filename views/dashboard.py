from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Sum,Q
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
import datetime
#create views of dashboard
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
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
    dashboard_year=[2016,2017,2018,2019,2020] # this list is to get the dropdown in dashboard
    try:
        curr_year = int(datetime.datetime.now().year)
        # low_year = int(curr_year-3)
        # high_year = int(curr_year+3)
        dashboard_year = [curr_year-3,curr_year-2,curr_year-1,curr_year,curr_year+1,curr_year+2,curr_year+3]
        try:
            low_year = int(obj_list.order_by('start_date')[:1].first().start_date.year)
        except:
            "Low year fetching error"
        try:
            high_year = int(obj_list.order_by('-end_date')[:1].first().end_date.year)
        except:
            "High year fetching error"
        if low_year<high_year and (low_year or high_year):
            if not low_year:
                low_year = int(curr_year-3)
            if not high_year:
                high_year = int(curr_year+3)
            dashboard_year=[]
            while high_year>=low_year:
                dashboard_year.append(low_year)
                low_year+=1
    except Exception as e:
        print "Datetime error",e
    #this is to filter based on cause area 
    # thsi method we are using in  corporatedashboard 
    ##
    if request.method == 'POST' :
        cause_area_id=request.POST.get('cause_area','') # this is to selecting  the causearea value based on dropdown list 
        dash_year=request.POST.get('dashboard_year','') # this is to selecting the year from dropdown list
    ##
    ##
    else:
        cause_area_id=request.GET.get('cause_area','') #this is to display the causearea in nextpages 
        dash_year=request.GET.get('dashboard_year','') #this is to display the year filter in nextpages
    if cause_area_id:
        cause_area_id = int(cause_area_id)
        obj_list=obj_list.filter(cause_area__id__in=[cause_area_id]) # this is to filter the selected causearea 
    if dash_year:
        dash_year=int(dash_year)
        dash_year_lower = datetime.datetime(year=dash_year,month=3,day=31)
        dash_year_higher = datetime.datetime(year=dash_year+1,month=4,day=1)
        print "dash_year",dash_year_lower," - ",dash_year_higher
        # obj_list=obj_list.filter(start_date__year__lte=dash_year,end_date__year__gte=dash_year) #this is filter the based on year
        obj_list=obj_list.filter( (Q(start_date__lte=dash_year_higher) & Q(end_date__gte=dash_year_lower)) )
    #    
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
    # this dictionary is for defining all abbrevationsof all states in India for sending proper data in json format
    state_abbr = {'ANDAMAN & NICOBAR ISLANDS':'AN','ARUNACHAL PRADESH':'AR','ANDHRA PRADESH':'AP','DAMAN & DIU':'DD','Chattisgarh':'CT','HARYANA':'HR','MAHARASHTRA':'MH','DADRA & NAGAR HAVELI':'DN','MADHYA PRADESH':'MP','TRIPURA':'TR','RAJASTHAN':'RJ','HIMACHAL PRADESH':'RJ','GUJARAT':'GJ','MEGHALAYA':'ML','KARNATAKA':'KA','PUNJAB':'PB','ODISHA':'OR','DELHI':'DL','JHARKHAND':'JH','Chandigarh':'CH','BIHAR':'BR','WEST BENGAL':'WB','MIZORAM':'MZ','UTTARAKHAND':'UT','UTTAR PRADESH':'UP','TAMIL NADU':'TN','TELANGANA':'TG','SIKKIM':'SK','JAMMU & KASHMIR':'JK','PONDICHERRY':'PY','NAGALAND':'NL','MANIPUR':'MN','LAKSHADWEEP':'LD','KERALA':'KL','GOA':'GA','ASSAM':'AS'}
    json_data = []
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
