from django.shortcuts import render
import requests,ast
import datetime
import json
from time import strptime
from django.contrib import messages
from calendar import monthrange
from projectmanagement.models import *
from projectmanagement.forms import *
from budgetmanagement.forms import TrancheForm
from budgetmanagement.models import Tranche
from media.models import Attachment,Keywords,FileKeywords
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.shortcuts import get_list_or_404, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from taskmanagement.views import total_tasks_completed,updates
from taskmanagement.models import Milestone
from pmu.settings import PMU_URL
from common_method import unique_slug_generator,add_keywords
# Create your views here.

def create_project(request):
    #Create and edit project (with dynamic activities)
    user_id = request.session.get('user_id')
    try:
        slug =  request.GET.get('slug')
        obj = Project.objects.get(slug=slug)
        form = ProjectForm(instance = obj)
        mapping_view = ProjectFunderRelation.objects.get(project=obj)
    except:
        form = ProjectForm()
    funder_user = UserProfile.objects.filter(active=2,organization_type=1)
    partner = UserProfile.objects.filter(active=2,organization_type=2)
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
            try:
                obj.created_by = UserProfile.objects.get(id=user_id)
            except:
                pass
            if not instance:
                obj.slug = unique_slug_generator(obj)
            obj.save()
            form.save_m2m()
            implementation_partner = request.POST.get('implementation_partner')
            funder = UserProfile.objects.get(id=request.POST.get('funder'))
            implementation_partner = UserProfile.objects.get(id=request.POST.get('implementation_partner'))
            if funder and implementation_partner:
                mapping = ProjectFunderRelation.objects.get_or_none(project=obj)
                if mapping:
                    mapping.funder=funder
                    mapping.implementation_partner=implementation_partner
                    mapping.total_budget=request.POST.get('total_budget')
                    mapping.save()
                else:
                    mapping = ProjectFunderRelation.objects.create(project=obj,funder=funder,\
                        implementation_partner=implementation_partner,total_budget=request.POST.get('total_budget'))
            return HttpResponseRedirect('/project/list/')
    return render(request,'project/project_edit.html',locals())

def project_list(request):
    user_id = request.session.get('user_id')
    user_obj = UserProfile.objects.get(user_reference_id = user_id )
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
    return render(request,'project/listing.html',locals())

def project_mapping(request):
    '''
    This function not in use
    '''
    form = ProjectMappingForm()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/dashboard/')
    return render(request,'project/project_mapping.html',locals())

def budget_tranche(request):
    '''
    This function is for Add budget tranche
    '''
    form = TrancheForm()
    slug =  request.GET.get('slug')
    user_id = request.session.get('user_id')
    project = Project.objects.get_or_none(slug=slug)
    form.fields["recommended_by"].queryset = UserProfile.objects.filter(is_admin_user=True)
    if request.method == 'POST':
        form = TrancheForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.project = project
            obj.save()
            return HttpResponseRedirect('/project/tranche/list/?slug=%s' %slug)
    return render(request,'budget/tranche.html',locals())

def tranche_list(request):
    slug =  request.GET.get('slug')
    obj = Project.objects.get(slug=slug)
    user_id = request.session.get('user_id')
    tranche_list = Tranche.objects.filter(project=obj,active=2)
    return render(request,'budget/listing.html',locals())

def key_parameter(request):
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

def add_parameter(request):
    '''
    This function is to add key parameter
    '''
    form = ProjectParameterForm()
    slug =  request.GET.get('slug')
    key =  request.GET.get('key')
    if request.method == 'POST':
        slug =  request.GET.get('slug')
        project = Project.objects.get(slug=slug)
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
        if name_count != 0:
            for i in range(name_count):
                name = 'name['+str(i+1)+']'
                instruction = 'instruction['+str(i+1)+']'
                obj = ProjectParameter.objects.create(parameter_type=parameter_type,project=project,instructions=request.POST.get(instruction),\
                        name=request.POST.get(name),parent=parent_obj,aggregation_function=request.POST.get('agg_type'))
        return HttpResponseRedirect('/project/parameter/manage/?slug=%s&key=2' %slug)
    return render(request,'project/add_key_parameter.html',locals())

def edit_parameter(request):
    '''
    This function is to Edit(add parameter, remove parameter and modify existing paramter)
    '''
    rem_id_list = []
    form = ProjectParameterForm()
    ids =  int(request.GET.get('id'))
    obj = ProjectParameter.objects.filter(active=2,parent=ids)
    parent_obj = ProjectParameter.objects.get_or_none(active=2,id=ids)
    if request.method == 'POST':
        rem_id = request.POST.get('rem_id')
        agg_type = request.POST.get('agg_type')
        para_type = request.POST.get('para_type')
        loop_count = request.POST.get('loop_count')
        name_count = request.POST.get('name_count')
        if rem_id != '':
            rem_id_list = map(int,str(rem_id).split(','))
            for i in rem_id_list:
                rem_obj = ProjectParameter.objects.get(id=i)
                rem_obj.switch()
                value_obj = ProjectParameterValue.objects.filter(keyparameter=rem_obj).delete()
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
        return HttpResponseRedirect('/project/parameter/manage/?slug=%s' %parent_obj.project.slug)
    return render(request,'project/edit_key_parameter.html',locals())

def upload_parameter(request):
    ids =  request.GET.get('id')
    key =  request.GET.get('key')
    parameter = ProjectParameter.objects.get(id=ids)
    key_parameter = ProjectParameter.objects.filter(active= 2,parent=parameter)
    key_parameter_list = [i.id for i in key_parameter]
    key_parameter_value = ProjectParameterValue.objects.filter(active= 2,keyparameter__in=key_parameter_list)
    existing_month = [k.start_date.month for k in key_parameter_value]
    start_date = parameter.project.start_date
    end_date = parameter.project.end_date
    month = ['January','February','March','April','May','June','July','August','September','October','November','December']
    month_id = [1,2,3,4,5,6,7,8,9,10,11,12]
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
                obj = ProjectParameterValue.objects.create(keyparameter=i,parameter_value=request.POST.get(value),\
                                start_date=date,end_date=end_date,submit_date=submit_date)
            parameter_value_list = sum(parameter_value_list)
            create_parameter_values = ProjectParameterValue.objects.create(keyparameter=parameter,parameter_value=parameter_value_list,\
                                start_date=date,end_date=end_date,submit_date=submit_date)
        else:
            obj = ProjectParameterValue.objects.create(keyparameter=parameter,parameter_value=request.POST.get('value'),\
                                start_date=date,end_date=end_date,submit_date=submit_date)
        return HttpResponseRedirect('/project/parameter/manage/?slug=%s&key=2' %parameter.project.slug)
    return render(request,'project/key_parameter.html',locals())

def manage_parameter(request):
    slug =  request.GET.get('slug')
    parameter = ProjectParameter.objects.filter(active= 2,project__slug=slug,parent=None)
    parameter_count = parameter.count()
    project_name = Project.objects.get(slug=slug).name
    return render(request,'project/parameter_list.html',locals())

def manage_parameter_values1(request):
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

def remove_record(request):
    url=request.META.get('HTTP_REFERER')
    ids =  request.GET.get('id')
    model =  eval(request.GET.get('model'))
    deact = model.objects.get(id=ids).switch()
    return HttpResponseRedirect(url)

def manage_parameter_values(request):
    ids =  request.GET.get('id')
    op = ProjectParameter.objects.get(id=ids)
    rr = ProjectParameterValue.objects.filter(active= 2,keyparameter__parent=op).order_by('id')
    names = ProjectParameter.objects.filter(active= 2,parent=op)
    title_list = []
    title_list.append('Month')
    newlist = sorted(rr, key=lambda x: x.submit_date, reverse=True)
    tot_len = rr.count()
    name_len = names.count()
    month_len=tot_len/name_len
    start = 1
    for j in rr:
        data=[]
        if start > month_len:
            data.append()
            start=start+1
    [title_list.append(str(i.name)) for i in names]

    
    lista = [['JAn','34','44','67'],['JAn','74','44','87']]

    return render(request,'project/parameter_value_list.html',locals())

def aggregate_project_parameters(param, values):
    '''
    Function to do calculations as per user selection (for key parameter values)
    '''
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
        aggr=aggr/cnt
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
            parent=ProjectParameterValue.objects.filter(active= 2,keyparameter_id=param.parent_id,period_id=val.period_id)
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

def project_total_budget(slug):
# to display the total budget ,disbursed,utilized percent in project summary page
    from taskmanagement.views import convert_budget
    try:
        project = Project.objects.get(slug=slug)
        budget = project.project_budget_details()
        planned_cost = budget.get('planned_cost') or 0
        utilized_cost = budget.get('utilized_cost') or 0
        disbursed_budget = budget.get('disbursed_cost') or 0
        total_percent = 100
        disbursed_percent = int((disbursed_budget/planned_cost)*100)
        utilized_percent = int((utilized_cost/planned_cost)*100)
    except:
        planned_cost= utilized_cost=disbursed_budget=total_percent= disbursed_percent=utilized_percent =0

    budget =  {'total':convert_budget(planned_cost),'disbursed':convert_budget(disbursed_budget),'utilized':convert_budget(utilized_cost),
    'total_percent':total_percent,'disbursed_percent':disbursed_percent,
    'utilized_percent':utilized_percent}
    return budget

def timeline_listing(obj):
# lisiting of timeline images function
    attach = Attachment.objects.filter(content_type = ContentType.objects.get_for_model(obj),
        object_id = obj.id,active=2,attachment_type= 1).order_by('date')
    return attach
    
def project_summary(request):
# to display the project details in project summary page
#Displaying pie chart detail
    image_url = PMU_URL
    slug =  request.GET.get('slug')
    user_id = request.session.get('user_id')
    user_obj = UserProfile.objects.get(user_reference_id = user_id)
    obj = Project.objects.get(slug = slug)
    activity = PrimaryWork.objects.filter(content_type=ContentType.objects.get(model="project"),object_id=obj.id)
    projectuserlist = ProjectUserRoleRelationship.objects.filter(project=obj)
    tasks = total_tasks_completed(obj.slug)
    updates_list = updates(Project.objects.filter(slug=slug))
    budget = project_total_budget(obj.slug)
    timeline = timeline_listing(obj)
    today = datetime.datetime.today()
    from datetime import timedelta

    milestone = Milestone.objects.filter(project__slug=slug,overdue__lte=today.now())
    timeline_json = []
    for i in timeline:
        data = {'date':i.date.strftime("%Y-%m-%d"),'name':i.description,'url':i.attachment_file.url if i.attachment_file else ''}
        timeline_json.append(data)
    for j in milestone:
        data = {'date':j.overdue.strftime("%Y-%m-%d"),'name':j.name,'url':''}
        timeline_json.append(data)
    timeline_json.sort(key=lambda item:item['date'], reverse=False)
    timeline_json_length = len(timeline_json)
    timeline_json = json.dumps(timeline_json)
    project_funders = ProjectFunderRelation.objects.get_or_none(project = obj)
    attachment = Attachment.objects.filter(object_id=obj.id,content_type=ContentType.objects.get(model='project'))
    image = PMU_URL
    parameter_count = ProjectParameter.objects.filter(active= 2,project=obj,parent=None).count()
    parameter_obj = ProjectParameter.objects.filter(active= 2,project=obj,parent=None)
    colors=['#5485BC', '#AA8C30', '#5C9384', '#981A37', '#FCB319','#86A033', '#614931', '#00526F', '#594266', '#cb6828', '#aaaaab', '#a89375']
    counter =0
    name_list = []
    para_name = {}
    pin_title_name = []
    pip_title_name = []
    number_json = []
    main_list = []
    for i in parameter_obj:
        if i.parameter_type=='NUM' or i.parameter_type=='PER' or i.parameter_type=='CUR':
            number = list(ProjectParameterValue.objects.filter(active= 2,keyparameter=i).values_list('parameter_value',flat=True))
            number = map(int,number)
            value = aggregate_project_parameters(i,number)
            data = {'title':i.name,'value':value,'type':i.parameter_type}
            number_json.append(data)
        elif i.parameter_type=='PIN' or i.parameter_type=='PIP':
            main_list = []
            pie_object = ProjectParameter.objects.filter(active= 2,parent=i)
            for y in pie_object:
                ttp= ProjectParameterValue.objects.filter(active= 2,keyparameter=y)
                values = list(ttp.values_list('parameter_value',flat=True))
                value = aggregate_project_parameters(pie_object[0],values)
                color = colors[counter]
                counter+=1
                main_list.append({'name': str(y.name),'y':value,'color':color})
        if main_list:
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
    ''' calling api to return the gantt chart format data '''
    data = {'project_id':int(obj.id)}
    rdd = requests.get(PMU_URL +'/managing/gantt-chart-data/', data=data)
    taskdict = ast.literal_eval(json.dumps(rdd.content))
    number_json = json.dumps(number_json)
    return render(request,'project/project-summary.html',locals())
    
def delete_upload_image(request):
    url=request.META.get('HTTP_REFERER')
    ids = request.GET.get('id')
    attach = Attachment.objects.get_or_none(id=int(ids))
    if attach :
        attach.active = 0
        attach.save()
    return HttpResponseRedirect(url)
