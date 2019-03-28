from django.shortcuts import render
import requests,ast
import datetime
import json
import pytz
from time import strptime
from django.contrib import messages
from calendar import monthrange
from projectmanagement.models import *
from projectmanagement.forms import *
from budgetmanagement.forms import get_tranche_form,TrancheForms
from budgetmanagement.models import (Tranche,ProjectReport,Budget,
                                    ProjectBudgetPeriodConf,BudgetPeriodUnit)
from media.models import Attachment,Keywords,FileKeywords,ProjectLocation,Comment
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from taskmanagement.views import total_tasks_completed,updates
from taskmanagement.models import Milestone,Activity,Task
from pmu.settings import (SAMITHA_URL,PMU_URL)
from common_method import unique_slug_generator,add_keywords,add_modified_by_user
from projectmanagement.templatetags.urs_tags import userprojectlist,get_funder,get_funder_mapping,get_pmo_user
from menu_decorators import check_loggedin_access
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import csv


# Views for projectmanagement
def manage_project_location(request,location_count,obj,city_var_list,rem_id_list):
    #this function is to manage project location 
    # 
    for i in range(location_count):
        city = 'city1_'+str(i+1)
        state = 'state_'+str(i+1)
        location_type = 'type_'+str(i+1)
        if city not in city_var_list:
            if request.POST.get(city):
                boundary_obj = Boundary.objects.get_or_none(id=request.POST.get(city))
            else:
                boundary_obj = Boundary.objects.get_or_none(id=request.POST.get(state))
            if boundary_obj:
                ProjectLocation.objects.create(location=boundary_obj,program_type=request.POST.get(location_type),content_type = ContentType.objects.get(model='project'),object_id=obj.id)
    ProjectLocation.objects.filter(id__in=rem_id_list).delete()

def project_location(request,obj,location):
    # this function is to add or 
    # edit location for project
    # 
    rem_id = request.POST.get('rem_id')
    city_var = request.POST.get('city_var')
    if rem_id != '':
        rem_id_list = map(int,str(rem_id).split(','))
    else:
        rem_id_list=[]
    if city_var != '':
        city_var_list = map(str,str(city_var).split(','))
    else:
        city_var_list = []
    if location:
        [ i.switch() for i in location]
    #if user not clicks on addmore location then by default it will 
    # take 1 location count
    try:
        location_count = int(request.POST.get('name_count'))
    except:
        location_count = 1
    manage_project_location(request,location_count,obj,city_var_list,rem_id_list)
    

def create_project(request):
    #Create and edit project (with dynamic activities)
    # 
    user_id = request.session.get('user_id')
    try:
        slug =  request.GET.get('slug')
        obj = Project.objects.get(slug=slug)
        form = ProjectForm(instance = obj)
        mapping_view = ProjectFunderRelation.objects.get(project=obj)
        location = ProjectLocation.objects.filter(object_id=obj.id,active=2)
        city_list = Boundary.objects.filter(boundary_level=3).order_by('name')
        keyss = ','.join([str(i.name) for i in ProjectParameter.objects.filter(is_beneficiary_type=True,active=2,project=obj)])
    except:
        form = ProjectForm()
        location = ''
    funder_user = UserProfile.objects.filter(active=2,organization_type=1,owner = True ) 
    # in funder_user added the owner field to remove the duplication from the dropdown
    # 
    #
    partner = UserProfile.objects.filter(active=2,organization_type=2,owner = True )
    #
    # in partner table added the field to remove the duplication of the user from dropdown 
    #
    state_list = Boundary.objects.filter(boundary_level=2).order_by('name')
    if request.method == 'POST':
        try:
            instance = get_object_or_404(Project, slug=slug)
            form = ProjectForm(request.POST,request.FILES or None, instance=instance)
        except:
            form = ProjectForm(request.POST,request.FILES)
            instance = ''
        if form.is_valid():
            obj = form.save(commit=False)
            obj.content_type = ContentType.objects.get(model="Program")
            obj.object_id = 0
            obj.request_status = 4
            obj.created_by = UserProfile.objects.get(user_reference_id=user_id)
            obj.slug = unique_slug_generator(obj,instance)
            obj.modified_by = user_id # added to save the modified by user (priya)
            if request.FILES.get('logo'):
                obj.logo=request.FILES.get('logo')
            obj.save()
            form.save_m2m()
            implementation_partner = request.POST.get('implementation_partner')
            funder = UserProfile.objects.get(id=request.POST.get('funder'))
            total_budget = request.POST.get('total_budget')
            ff = funder_mapping(funder,implementation_partner,total_budget,obj)
            project_location(request,obj,location)
            keywords=request.POST.get('keywords') #this is to create the projectparameters
            key_list=keywords.split(',')
            para=get_parameter_keywords(keywords,key_list,obj)# this function is to get the projectparameter keywords
            
            return HttpResponseRedirect('/project/list/')
    return render(request,'project/project_add.html',locals())
#
#
# here the project/list is the url we are redirecting the page from add/edit page to listing page 
#
# 
# this function is to list of projectparameter keywords
#this function is to update the projectparamter keywords
##
def get_parameter_keywords(keywords,key_list,obj):
    # here we are passing the keywords 
    # here by using split we are changing to keywords to key_list
    for i in key_list:
        para_obj=ProjectParameter.objects.get_or_none(parameter_type='NUM',name__iexact=i,project=obj,active=2)
        if para_obj:
            para_obj.is_beneficiary_type=True
            para_obj.save()
        else:
            para_obj,status=ProjectParameter.objects.get_or_create(parameter_type='NUM',name =i,project=obj,is_beneficiary_type=True,active=2)
        #this is to change the beneficiary type as false
        para_obj=ProjectParameter.objects.filter(parameter_type='NUM',project=obj,active=2).exclude(name__in=key_list)
        if para_obj:
            para_obj.update(is_beneficiary_type=False)  
    return para_obj
##
##
def funder_mapping(funder,implementation_partner,total_budget,obj):
    #this function is to map implementation partner and funder
    # 
    implementation_partner = UserProfile.objects.get(id=implementation_partner)
    mapping = ProjectFunderRelation.objects.get_or_none(project=obj)
    # mapping of implementation partner and funder for project
    if mapping:
        mapping.funder=funder
        mapping.implementation_partner=implementation_partner
        mapping.total_budget= total_budget
        mapping.save()
    else:
        mapping = ProjectFunderRelation.objects.create(project=obj,funder=funder,\
            implementation_partner=implementation_partner,total_budget=total_budget)
    return mapping

def pagination(request, plist):
    paginator = Paginator(plist, 10)
    page = request.GET.get('page', 1)
    try:
        plist = paginator.page(page)
    except PageNotAnInteger:
        plist = paginator.page(1)
    except EmptyPage:
        plist = paginator.page(paginator.num_pages)
    return plist

def project_list(request):
    '''
    This function is to list all project created by logged in user
    '''
    user_id = request.session.get('user_id')
    logged_user_obj = UserProfile.objects.get(user_reference_id = user_id )
    obj_list = userprojectlist(logged_user_obj)
    # for download the csv report
    if request.GET.get('download') == 'true':
        return get_project_report(obj_list)
    obj_list = pagination(request,obj_list)
    return render(request,'project/listing.html',locals())


#  csv of project listing with locations
def get_project_report(projects):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Project_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Start Date','End Date','Project Name','Managed by','Implementation Partner','Funder','Status','Planned Budget','Allocated Budget',
    				'Cause Area','Beneficiary Types','No of Beneficiaries planned','No of Beneficiaries served','Locations'])
    for pro in projects:
        funder_mapping = get_funder_mapping(pro)
        org_name = get_pmo_user(pro)
        writer.writerow([pro.start_date, pro.end_date, pro.name,org_name,funder_mapping.implementation_partner.organization,
         funder_mapping.funder.organization, pro.get_active_display(),pro.total_budget, pro.project_budget_details().get('planned_cost'),pro.get_cause_area(),
		 pro.get_beneficiary(),pro.no_of_beneficiaries,pro.project_parameter_value(),pro.get_locations()])
    return response

# alternative for download of project report csv
def alternative_project_report(projects):
    import os
    from django.conf import settings
    data = open(os.path.join(settings.BASE_DIR,'static/project_report/Project_report.csv'),'w+')
    response = HttpResponse(data, content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename=Project_report.csv'
    writer = csv.writer(response)
    writer.writerow(['Start Date','End Date','Project Name','Managed by','Implementation Partner','Funder','Status','Budget Planned',
    				'Cause Area','No of Beneficiares','Beneficiary Types','Locations','Duration'])
    for pro in projects:
        funder_mapping = get_funder_mapping(pro)
        org_name = get_pmo_user(pro)
        writer.writerow([pro.start_date, pro.end_date, pro.name,org_name,funder_mapping.implementation_partner.organization,
         funder_mapping.funder.organization, pro.get_active_display(), pro.total_budget,pro.get_cause_area(),pro.no_of_beneficiaries,
		 pro.get_beneficiary(),pro.get_locations(),pro.duration])
    return response

# get PMO user

    
def get_project_budget_utilized_amount(projectobj,budgetobj):
#    to get the project utilized amount for budget 
    budget_periodlist = ProjectBudgetPeriodConf.objects.filter(project = projectobj,budget = budgetobj,active=2).values_list('id', flat=True)
    budget_period_utilizedamount = BudgetPeriodUnit.objects.filter(budget_period__id__in=budget_periodlist).values_list('utilized_unit_cost', flat=True)
    budget_period_utilizedamount = map(lambda x:x if x else 0,budget_period_utilizedamount)
    final_budget_period_utilizedamount = sum(map(float,budget_period_utilizedamount))
    return final_budget_period_utilizedamount

def auto_update_tranche_amount(final_budget_utilizedamount,project):
    # this function is to auto updte tranche amount
    tranchelist = Tranche.objects.filter(project=project,active=2).order_by("disbursed_date")
    for i in tranchelist:
        i.utilized_amount = 0
        i.save()
        if final_budget_utilizedamount > 0:
            if i.actual_disbursed_amount< final_budget_utilizedamount:
                i.utilized_amount = i.actual_disbursed_amount
                i.save()
                final_budget_utilizedamount = final_budget_utilizedamount-i.utilized_amount
            else:
                i.utilized_amount = final_budget_utilizedamount 
                i.save()
                final_budget_utilizedamount = 0
    return tranchelist

@check_loggedin_access
def budget_tranche(request):
    '''
    This function is for Add budget tranche
    '''
    
    slug =  request.GET.get('slug')
    form = TrancheForms()
    try:
        tranche_id =  request.GET.get('tranche_id')
        obj = Tranche.objects.get_or_none(id=tranche_id)
        form = TrancheForms(instance = obj)
        comment = Comment.objects.get(content_type = ContentType.objects.get(model='tranche'),object_id=obj.id)
    except:
        pass
    user_id = request.session.get('user_id')
    project = Project.objects.get_or_none(slug=slug)
    tt = ProjectUserRoleRelationship.objects.filter(project=project)
    funder = ProjectFunderRelation.objects.get(project=project)
    list1 = [i.user.id for i in tt]
    list1.append(int(funder.funder.id))
    list1.append(int(funder.implementation_partner.id))
    recommended_by = UserProfile.objects.filter(id__in=list(set(list1)))
    if request.method == 'POST':
        tranche_id = request.POST.get('tranche_id')
        try:
            instance = get_object_or_404(Tranche, id=tranche_id)
            form = TrancheForms(request.POST,request.FILES or None, instance=instance)
        except:
            form = TrancheForms(request.POST,request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.project = project
            obj.recommended_by = UserProfile.objects.get(id=request.POST.get('recommended_by'))
            add_modified_by_user(obj,request)
            obj.save()

            Comment.objects.create(active=2,content_type = ContentType.objects.get(model='tranche'),object_id=obj.id,text=request.POST.get('comment'))
            budgetobj = Budget.objects.latest_one(project = project,active=2)
            final_budget_utilizedamount = get_project_budget_utilized_amount(project,budgetobj)
            auto_update_tranche_amount(final_budget_utilizedamount,project)
            return HttpResponseRedirect('/project/tranche/list/?slug=%s' %slug)
    return render(request,'budget/tranche.html',locals())

@check_loggedin_access
def tranche_list(request):
    '''
    This function is for listing of project tranches                                
    '''
    slug =  request.GET.get('slug')
    obj = Project.objects.get(slug=slug)
    user_id = request.session.get('user_id')
    tranche_list = Tranche.objects.filter(project=obj,active=2).order_by("disbursed_date")
    user = UserProfile.objects.get_or_none(user_reference_id = user_id)
    from taskmanagement.views import get_assigned_users
    status = get_assigned_users(user,obj)
    key = request.GET.get('key')
    projectobj = obj
    project_location = ProjectLocation.objects.filter(active=2,content_type = ContentType.objects.get(model='project'),object_id=projectobj.id)
    return render(request,'budget/listing.html',locals())

def key_parameter(request):
    '''
    This function is to add new parameter for project
    '''
    user_id = request.session.get('user_id')
    slug =  request.GET.get('slug')
    proj_obj = Project.objects.filter(created_by=UserProfile.objects.get(id=3))
    if request.method == 'POST':
        project = int(request.POST.get('project'))
        parameter_type = request.POST.get('para_type')
        value = request.POST.get('value')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        attachment = request.POST.get('attachment')
        parameter_obj = ProjectParameter.objects.create(parameter_type=str(parameter_type),project=Project.objects.get(id=project),name=request.POST.get('name'))
        parameter_value = ProjectParameterValue.objects.create(keyparameter=parameter_obj,\
                    parameter_value=value,start_date=start_date,end_date=end_date)
    return render(request,'project/key_parameter.html',locals())
@check_loggedin_access
def add_parameter(request):
    '''
    This function is to add key parameter for project
    '''
    form = ProjectParameterForm()
    slug =  request.GET.get('slug') or request.POST.get('slug')
    key =  request.GET.get('key')
    project = Project.objects.get(slug=slug)
    if request.method == 'POST':
        slug =  request.GET.get('slug')
        parameter_type = request.POST.get('para_type')
        name = request.POST.get('name')
        instruction = request.POST.get('instruction')
        name_count = int(request.POST.get('name_count'))
        agg_type = request.POST.get('agg_type')
        if parameter_type == 'NUM' or parameter_type == 'PER' or parameter_type == 'CUR':
            agg_type = 'ADD'
        parent_obj = ProjectParameter.objects.create(parameter_type=parameter_type,\
                                project=project,aggregation_function=agg_type,name = name,\
                                instructions=instruction)
        # to save modified_by user to get the updates 
        add_modified_by_user(parent_obj,request)
        if name_count != 0:
            for i in range(name_count):
                name = 'name['+str(i+1)+']'
                instruction = 'instruction['+str(i+1)+']'
                obj = ProjectParameter.objects.create(parameter_type=parameter_type,project=project,instructions=request.POST.get(instruction),\
                        name=request.POST.get(name),parent=parent_obj,aggregation_function=request.POST.get('agg_type'))
        return HttpResponseRedirect('/project/parameter/manage/?slug=%s&key=2' %slug)
    return render(request,'project/add_key_parameter.html',locals())

def delete_parameter(rem_id_list):
    # this function is to delete parameter. 
    # Pass parameter id in list
    # 
    for i in rem_id_list:
        rem_obj = ProjectParameter.objects.get(id=i)
        rem_obj.switch()
        ProjectParameterValue.objects.filter(keyparameter=rem_obj).delete()
        
@check_loggedin_access
def edit_parameter(request):
    # This function is to Edit(add parameter, remove 
    # parameter and modify existing paramter)
# 
    rem_id_list = []
    form = ProjectParameterForm()
    ids =  int(request.GET.get('id'))
    obj = ProjectParameter.objects.filter(active=2,parent=ids)
    slug = request.GET.get('slug') or request.POST.get('slug')
    parent_obj = ProjectParameter.objects.get_or_none(active=2,id=ids)
    project = Project.objects.get(slug=slug)
    if request.method == 'POST':
        rem_id = request.POST.get('rem_id')
        agg_type = request.POST.get('agg_type')
        para_type = request.POST.get('para_type')
        loop_count = request.POST.get('loop_count')
        name_count = request.POST.get('name_count')
        parent_obj.name = request.POST.get('name')
        parent_obj.instructions = request.POST.get('instruction')
        if rem_id != '':
            rem_id_list = map(int,str(rem_id).split(','))
            del_para = delete_parameter(rem_id_list)
        for j in obj:
            if j.id not in rem_id_list:
                name = 'name['+str(j)+']'
                instruction = 'instruction['+str(j)+']'
                modify = ProjectParameter.objects.get(id=j.id)
                modify.name = request.POST.get(name)
                modify.instructions = request.POST.get(instruction)
                modify.aggregation_function = request.POST.get('agg_type')
                modify.save()
        if name_count:
            i=int(loop_count)
            for i in range(int(loop_count),int(name_count)):
                name = 'name['+str(i+1)+']'
                instruction = 'instruction['+str(i+1)+']'
                create_parameter = ProjectParameter.objects.create(name=request.POST.get(name),project=parent_obj.project,\
                            parent=parent_obj,instructions=request.POST.get(instruction),aggregation_function=agg_type,\
                            parameter_type=parent_obj.parameter_type)
        parent_obj.save()
        # to save modified_by user to get the updates in updates section
        add_modified_by_user(parent_obj,request)
        return HttpResponseRedirect('/project/parameter/manage/?slug=%s' %parent_obj.project.slug)
    return render(request,'project/edit_key_parameter.html',locals())

import calendar

@check_loggedin_access
def upload_parameter(request):
    # This function is to add values to key parameter which 
    # are added by admin (parameters number is dynamic)
    # 
    ids =  request.GET.get('id')
    key =  request.GET.get('key')
    slug = request.GET.get('slug') or request.POST.get('slug')
    parameter = ProjectParameter.objects.get(id=ids)
    project = parameter.project
    strt = project.start_date.year
    end = project.end_date.year
    key_parameter = ProjectParameter.objects.filter(active= 2,parent=parameter)
    key_parameter_list = [i.id for i in key_parameter]
    key_parameter_value = ProjectParameterValue.objects.filter(active= 2,keyparameter__in=key_parameter_list)
    existing_month = [k.start_date.month for k in key_parameter_value]
    start_date = parameter.project.start_date
    
    end_date = parameter.project.end_date
    month = ['January','February','March','April','May','June','July','August','September','October','November','December']
    month_id = [1,2,3,4,5,6,7,8,9,10,11,12]
    parameter_month = ProjectParameterValue.objects.filter(active=2,keyparameter=parameter)
    parameter_value_month = [calendar.month_name[i.start_date.month] for i in parameter_month]
    month_zip = zip(month,month_id)
    if request.method == 'POST':
        month = request.POST.get('month')
        year = int(request.POST.get('year'))
        month = strptime(month[:3],'%b').tm_mon
        now = datetime.datetime.now()
        date = str(year)+'-'+str(month)+'-'+'1'
        days = monthrange(now.year, month)[1]
        end_date = str(year)+'-'+str(month)+'-'+str(days)
        submit_date = str(year)+'-'+str(now.month)+'-'+str(now.day)
        if key_parameter.exists():
            total_count = []
            parameter_value_list = []
            for i in key_parameter:
                value = 'value['+str(i.id)+']'
                parameter_value_list.append(int(request.POST.get(value)))
                obj = ProjectParameterValue.objects.create(active=2, keyparameter=i,parameter_value=request.POST.get(value),\
                                start_date=date,end_date=end_date,submit_date=submit_date)
                add_modified_by_user(obj,request)
            parameter_value_list = sum(parameter_value_list)
            create_parameter_values = ProjectParameterValue.objects.create(keyparameter=parameter,parameter_value=parameter_value_list,\
                                start_date=date,end_date=end_date,submit_date=submit_date)
            add_modified_by_user(create_parameter_values,request)
        else:
            obj = ProjectParameterValue.objects.create(keyparameter=parameter,parameter_value=request.POST.get('value'),\
                                start_date=date,end_date=end_date,submit_date=submit_date)
            add_modified_by_user(obj,request)
        return HttpResponseRedirect('/project/parameter/manage/?slug=%s&key=2' %parameter.project.slug)
    return render(request,'project/key_parameter.html',locals())

@check_loggedin_access
def edit_parameter_values(request):
    # edit_value
    slug=request.GET.get('slug') or request.POST.get('slug')
    project = Project.objects.get(slug=slug)
    ids =  request.GET.get('id')
    date1 = request.GET.get('month')
    date = request.GET.get('month').split(' ')
    month_no = strptime(date[0],'%B').tm_mon
    year = int(date[1])
    start_date=str(year)+str(month_no)
    date_obj = datetime.datetime.strptime(start_date, "%Y%m")
    parameter = ProjectParameter.objects.get(id=ids)
    single_parameter = ProjectParameterValue.objects.get(active= 2,keyparameter=parameter,start_date=date_obj)
    key_parameter = ProjectParameter.objects.filter(active= 2,parent=parameter)
    key_parameter_list = [i.id for i in key_parameter]
    key_parameter_value = list(ProjectParameterValue.objects.filter(active= 2,keyparameter__in=key_parameter_list,start_date=date_obj))
    main_para = zip(key_parameter,key_parameter_value)
    if request.GET.get('key') == '1':
        for i in key_parameter_value:
            i.switch()
        parent_parameter=ProjectParameterValue.objects.get(active=2,keyparameter=parameter,start_date=date_obj)
        parent_parameter.active=0
        parent_parameter.save()
        return HttpResponseRedirect('/project/parameter/values/manage/?id={}&slug={}'.format(parameter.id,slug))
    if request.method == 'POST':
        if key_parameter_value != []:
            for i in key_parameter_value:
                parameter_obj = ProjectParameterValue.objects.get(active=2,id=i.id)
                parameter_obj.parameter_value = request.POST.get(str(i.id))
                parameter_obj.save()
        else:
            single_parameter.parameter_value = request.POST.get('value')
            single_parameter.save()
        return HttpResponseRedirect('/project/parameter/values/manage/?id={}&slug={}'.format(parameter.id,slug))
    return render(request,'project/key_parameter.html',locals())
    
@check_loggedin_access
def manage_parameter(request):
    # 
    # This function is to manange(list) all 
    # key parameter for perticular project
    # 
    slug =  request.GET.get('slug')
    parameter = ProjectParameter.objects.filter(active= 2,project__slug=slug,parent=None)
    parameter_count = parameter.count()
    projectobj = Project.objects.get(slug=slug)
    project_name = projectobj.name
    return render(request,'project/parameter_list.html',locals())

def manage_parameter_values1(request):
    # This function not in use
    # 
    ids =  request.GET.get('id')
    parameter = ProjectParameter.objects.get(id=ids)
    parameter_count = ProjectParameter.objects.filter(active= 2,parent=parameter).count() + 1
    if parameter.parameter_type == 'NUM' or parameter.parameter_type == 'CUR' or parameter.parameter_type == 'PER':
        ff = ProjectParameterValue.objects.filter(active= 2,keyparameter=parameter)
    else:
        child_parameter = ProjectParameterValue.objects.filter(active= 2,keyparameter__parent=parameter).order_by('-submit_date')
    name_range = range(1,parameter_count)
    values_list = child_parameter.values_list('parameter_value',flat=True)
    values = aggregate_project_parameters(parameter,child_parameter)
    return render(request,'project/parameter_value_list.html',locals())

# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.

@check_loggedin_access
def remove_record(request):
    # This is common method to delete(deactivate) record from db. 
    # Pass model name and its id
    #
	url=request.META.get('HTTP_REFERER')
	ids =  request.GET.get('id')
	from django.apps import apps
        data={'Project':'projectmanagement','Task':'taskmanagement',
              'Budget':'budgetmanagement','Userprofile':'userprofile',
              'Media':'media','Activity':'taskmanagement',
              'Milestone':'taskmanagement','Tranche':'budgetmanagement',
              'ProjectReport':'budgetmanagement','Attachment':'media',
              'Keywords':'media','ProjectParameter':'projectmanagement'}
	app_label=data.get(request.GET.get(str('model')))
	model = apps.get_model(app_label,request.GET.get(str('model')))
	deact = model.objects.get(id=ids).switch()
	if request.GET.get('model') == 'ProjectReport':
		model.objects.get(id=ids).delete_report_answers()
	if request.GET.get('model') == 'Tranche':
		deact = model.objects.get(id=ids)
		project = Project.objects.get(id=int(deact.project.id))
		budgetobj = Budget.objects.latest_one(project = project,active=2)
		final_budget_utilizedamount = get_project_budget_utilized_amount(project,budgetobj)
		auto_update_tranche_amount(final_budget_utilizedamount,project)
	return HttpResponseRedirect(url)

@check_loggedin_access
def manage_parameter_values(request):
    # This function is to get all parameter values 
    # for perticular key parameter
    # 
    slug = request.GET.get('slug')
    ids =  request.GET.get('id')
    parameter = ProjectParameter.objects.get(id=ids)
    project = ProjectParameter.objects.get(id=ids).project
    strt = project.start_date.year
    end = project.end_date.year
    parameter_value = ProjectParameterValue.objects.filter(active= 2,keyparameter__parent=parameter).order_by('id')
    names = ProjectParameter.objects.filter(active= 2,parent=parameter)
    title_list = []
    title_list.append('Month')
    import calendar
    master_data = []
    if parameter_value.exists():
        for l in range(strt,end+1):
            for k in range(1,13):
                data = []
                obj = parameter_value.filter(start_date__month=k,start_date__year=l)
                if obj.exists():
                    month_name = calendar.month_name[k] +' '+ str(l)
                    data.append(month_name)
                    [ data.append(int(u.parameter_value)) for u in obj]
                master_data.append(data)
            master_data = filter(None, master_data)
    else:
        obj = ProjectParameterValue.objects.filter(active=2,keyparameter=parameter)
        data = []
        for j in obj:
            month = calendar.month_name[j.start_date.month] + ' ' + str(j.start_date.year)
            value = j.parameter_value
            master_data.append([month,value])
    [title_list.append(str(i.name)) for i in names]
    return render(request,'project/parameter_value_list.html',locals())

# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
def aggregate_project_parameters(param, values):
    # Function to do calculations as per 
    # user selection (for key parameter values)
    # 
    ret={}
    aggr=0
    if param.aggregation_function=='ADD':
        for val in values:
            aggr+= int(val)
    elif param.aggregation_function=='AVG' :
        cnt=0
        for val in values:
            cnt+=1
            aggr += int(val)
        aggr=aggr/cnt if cnt >0 else 0
    elif param.aggregation_function == "WAV":
        paggr=0
        for val in values:
            parent=ProjectParameterValue.objects.filter(active= 2,keyparameter=param.parent_id)
            parent_parameter = sum(map(int,parent.values_list('parameter_value',flat=True)))
            aggr+=int(val)*parent_parameter
            paggr+=parent_parameter
        aggr=aggr/paggr
    elif param.aggregation_function == "WAP":
        paggr=0
        for val in values:
            parent=ProjectParameterValue.objects.filter(active= 2,keyparameter_id=param.parent_id)
            parent_parameter = sum(map(int,parent.values_list('parameter_value',flat=True)))
            aggr+=int(val)*parent_parameter
            paggr+=parent_parameter
        aggr=aggr/paggr
    ret['name']=param.name
    ret['parameter_type']= param.parameter_type
    ret['instructions'] = param.instructions
    ret['aggregate_value'] = aggr
    ret['parent_name'] = None if param.parent is None else param.parent.name
    return aggr

# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
def project_total_budget(slug):
    # to display the total budget ,disbursed,
    # utilized percent in project summary page
    # 
    from taskmanagement.views import convert_budget
    try:
        project = Project.objects.get(slug=slug)
        budget = project.project_budget_details()
        planned_cost = budget.get('planned_cost') or '0'
        utilized_cost = budget.get('utilized_cost') or '0'
        disbursed_budget = budget.get('disbursed_cost') or '0'
        total_percent = 100
        disbursed_percent = int((float(disbursed_budget)/planned_cost)*100)
        utilized_percent = int((float(utilized_cost)/planned_cost)*100)
    except:
        planned_cost= utilized_cost=disbursed_budget=total_percent= disbursed_percent=utilized_percent ='0'

    budget =  {'total':str(convert_budget(planned_cost)),'disbursed':str(convert_budget(disbursed_budget)),'utilized':str(convert_budget(utilized_cost)),
    'total_percent':total_percent,'disbursed_percent':disbursed_percent,
    'utilized_percent':utilized_percent}
    return budget

def timeline_listing(obj):
# lisiting of timeline images function
# 
    attach = Attachment.objects.filter(content_type = ContentType.objects.get_for_model(obj),
        object_id = obj.id,active=2,attachment_type= 1,timeline_progress=True).order_by('date')
    return attach

def get_timeline_process(timeline,milestone):
    # this function is to get json data for timeline progrsss
    # in project summary page
    timeline_json = []
    for i in timeline:
        data = {'date':i.date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d"),'type':'image','name':i.description,'url':i.attachment_file.url if i.attachment_file else '','id':i.id}
        timeline_json.append(data)
    for j in milestone:
        data = {'date':j.overdue.strftime("%Y-%m-%d"),'name':j.name,'url':'','type':'milestone','id':''}
        timeline_json.append(data)
    timeline_json.sort(key=lambda item:item['date'], reverse=False)
    timeline_json_length = len(timeline_json)
    timeline_json = json.dumps(timeline_json)
    return timeline_json,timeline_json_length

@check_loggedin_access
def project_summary(request):
#
# to display the project details in project summary page                    
#Displaying pie chart detail
#   
    image_url = PMU_URL
    slug =  request.GET.get('slug')
    user_id = request.session.get('user_id')
    user_obj = UserProfile.objects.get(user_reference_id = user_id)
    obj = Project.objects.get(slug = slug)
    projectobj = obj
    activity = Activity.objects.filter(project=obj)
    projectuserlist = ProjectUserRoleRelationship.objects.filter(active=2,project=obj)
    tasks = total_tasks_completed(obj.slug)
    updates_list = updates(Project.objects.filter(slug=slug))
    budget = project_total_budget(obj.slug)
    timeline = timeline_listing(obj)
    today = datetime.datetime.today()
    milestone = Milestone.objects.filter(project__slug=slug,overdue__lte=today.now())
    timeline_json,timeline_json_length = get_timeline_process(timeline,milestone)
    year_min = 2000
    year_max = 3000
    global year_min, year_max
    try:
        years = request.GET.getlist('year')
        year_min = min(years)
        year_max = max(years)
    except Exception as y:
        y.message
    from taskmanagement.views import get_assigned_users
    status = get_assigned_users(user_obj,obj)
    key = request.GET.get('key')
    project_funders = ProjectFunderRelation.objects.get_or_none(project = obj)
    attachment = Attachment.objects.filter(object_id=obj.id,content_type=ContentType.objects.get(model='project'))
    image = PMU_URL
    parameter_count = ProjectParameter.objects.filter(active= 2,project=obj,parent=None).count()
    parameter_obj = ProjectParameter.objects.filter(active= 2,project=obj,parent=None)
    master_pip,master_pin,pin_title_name,pip_title_name,number_json,master_sh = parameter_pie_chart(parameter_obj)
    ''' calling api to return the gantt chart format data '''
    funderobj = get_funder(obj)
    data = {'project_id':int(obj.id),'company_name':str(funderobj.funder.organization) if funderobj else '','start_date':'','end_date':''}
    rdd = requests.get(PMU_URL +'/managing/gantt-chart-data/', data=data)
    taskdict = ast.literal_eval(json.dumps(rdd.content))
    number_json1 = number_json
    number_json = json.dumps(number_json)
    return render(request,'project/project-summary.html',locals())
    
def parameter_pie_chart(parameter_obj):
    # This function is to get pie chart information 
    # in json data (both pie chart type)
    # 
    name_list = []
    para_name = {}
    pin_title_name = []
    pip_title_name = []
    number_json = []
    main_list = []
    for i in parameter_obj:
        if i.parameter_type=='NUM' or i.parameter_type=='PER' or i.parameter_type=='CUR':
            try: 
                number = list(ProjectParameterValue.objects.filter(active= 2,keyparameter=i,start_date__year__gte=year_min,end_date__year__lte=year_max).values_list('parameter_value',flat=True))
            except:
                number = list(ProjectParameterValue.objects.filter(active= 2,keyparameter=i).values_list('parameter_value',flat=True))
            number = map(int,number)
            value = aggregate_project_parameters(i,number)
            data = {'title':i.name,'value':value,'type':i.parameter_type}
            number_json.append(data)
        elif i.parameter_type=='PIN' or i.parameter_type=='PIP':
            main_list = pie_chart_mainlist(i)
        if i.parameter_type in para_name:
            para_name[i.parameter_type].append(main_list)
        else:
            para_name.setdefault(i.parameter_type,[])
            para_name[i.parameter_type].append(main_list)
            name_list.append(str(i.name))
        if i.parameter_type == 'PIN':
            pin_title_name.append(str(i.name))
        if i.parameter_type == 'PIP':
            pip_title_name.append(str(i.name))
    master_sh = para_name
    master_sh_len = {key:len(values) for key,values in master_sh.items()}
    master_pin = map(lambda x: "Batch_size_" + str(x), range(master_sh_len.get('PIN',0)))
    master_pip = map(lambda x: "Beneficary_distribution_"+ str(x), range(master_sh_len.get('PIP',0)))
    
    return master_pip,master_pin,pin_title_name,pip_title_name,number_json,master_sh

def pie_chart_mainlist(obj):
    # This function is to get pie chart information 
    # in json data (both pie chart type)
    # 
    colors=['#5485BC', '#AA8C30', '#5C9384', '#981A37', '#FCB319','#86A033', '#614931', '#00526F', '#594266', '#cb6828', '#aaaaab', '#a89375']
    main_list = []
    counter =0
    pie_object = ProjectParameter.objects.filter(active= 2,parent=obj)
    for y in pie_object:
        try:
            values = list(ProjectParameterValue.objects.filter(active= 2,keyparameter=y,start_date__year__gte=year_min,end_date__year__lte=year_max).values_list('parameter_value',flat=True))
        except:
            values = list(ProjectParameterValue.objects.filter(active= 2,keyparameter=y,).values_list('parameter_value',flat=True))
        value = aggregate_project_parameters(pie_object[0],values)
        color = colors[counter]
        counter+=1
        main_list.append({'name': str(y.name),'y':value,'color':color})

    return main_list

def pie_chart_mainlist_report(obj,start_date,end_date):
    '''
    This function is to get pie chart information in json data (both pie chart type)
    '''
    colors=['#5485BC', '#AA8C30', '#5C9384', '#981A37', '#FCB319','#86A033', '#614931', '#00526F', '#594266', '#cb6828', '#aaaaab', '#a89375']
    main_list = []
    counter =0
    pie_object = ProjectParameter.objects.filter(active= 2,parent=obj)
    for y in pie_object:
        try:
            values = list(ProjectParameterValue.objects.filter(active= 2,keyparameter=y, start_date__gte=start_date,end_date__lte=end_date).values_list('parameter_value',flat=True))
        except:
            values = list(ProjectParameterValue.objects.filter(active= 2,keyparameter=y).values_list('parameter_value',flat=True))
        if values:
            value = aggregate_project_parameters(pie_object[0],values)
            color = colors[counter]
            counter+=1
            main_list.append({'name': str(y.name),'y':value,'color':color})
    return main_list


# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
def delete_upload_image(request):
    # this function is to delete image from timeline                                
    # 
    url=request.META.get('HTTP_REFERER')
    ids = request.GET.get('id')
    attach = Attachment.objects.get_or_none(id=int(ids))
    if attach :
        attach.active = 0
        attach.save()
    return HttpResponseRedirect(url)


##to change the beneficary type as true##
def beneficiary_type():
    bene_type=ProjectParameter.objects.filter(name__icontains='Beneficiary')
    for i in bene_type:
        i.bene_type=True
        i.save()

#    The dict type has been reimplemented to use a more compact 
# representation based on a proposal by Raymond Hettinger and 
# similar to the PyPy dict implementation. 
# This resulted in dictionaries using 20% to 25% less memory
# when compared to Python 3.5.
#    Customization of class creation has been simplified with the new protocol.
#    The class attribute definition order is now preserved.
#    The order of elements in **kwargs now corresponds to 
# the order in which keyword arguments were passed to the function.
#    DTrace and SystemTap probing support has been added.
#    The new PYTHONMALLOC environment variable can now 
# be used to debug the interpreter memory allocation and access errors.

#Significant improvements in the standard library:

#    The asyncio module has received new features, 
# significant usability and performance improvements, and a
 # fair amount of bug fixes. Starting with Python 3.6 the 
 # asyncio module is no longer provisional and its API is considered stable.
#    A new file system path protocol has been implemented 
# to support path-like objects. All standard library functions 
# operating on paths have been updated to work with the new protocol.
#    The datetime module has gained support for Local Time Disambiguation.
#    The typing module received a number of improvements.
#    The tracemalloc module has been significantly reworked 
# and is now used to provide better output for ResourceWarning 
# as well as provide better diagnostics for memory allocation errors. 
# See the PYTHONMALLOC section for more information.

#Security improvements:

#    The new secrets module has been added to simplify 
# the generation of cryptographically strong pseudo-random 
# numbers suitable for managing secrets such as account authentication,
# tokens, and similar.
#    On Linux, os.urandom() now blocks until the system urandom 
# entropy pool is initialized to increase the security. 
# See the PEP 524 for the rationale.
#    The hashlib and ssl modules now support OpenSSL 1.1.0.
#    The default settings and feature set of the ssl module have been improved.
#    The hashlib module received support for the BLAKE2, SHA-3 
# and SHAKE hash algorithms and the scrypt() key derivation function.



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
