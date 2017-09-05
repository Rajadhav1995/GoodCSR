import requests
import json, ast
from django.shortcuts import render
import datetime
from django.contrib import messages
from calendar import monthrange
from projectmanagement.models import *
from projectmanagement.forms import *
from budgetmanagement.forms import TrancheForm
from budgetmanagement.models import Tranche
from media.forms import AttachmentForm,ImageUpload
from media.models import Attachment,Keywords,FileKeywords
from django.http import HttpResponseRedirect
from django.shortcuts import get_list_or_404, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from taskmanagement.views import total_tasks_completed,updates
from pmu.settings import PMU_URL
from projectmanagement.utils import random_string_generator
# Create your views here.

def create_project(request):
    user_id = request.session.get('user_id')
    try:
        slug =  request.GET.get('slug')
        obj = Project.objects.get(slug=slug)
        form = ProjectForm(instance = obj)
        mapping_view = ProjectFunderRelation.objects.get(project=obj)
        activity_view = PrimaryWork.objects.filter(object_id=obj.id,content_type=ContentType.objects.get(model="project"))
    except:
        form = ProjectForm()
    # import ipdb;ipdb.set_trace()
    funder_user = UserProfile.objects.filter(active=2,organization_type=1)
    partner = UserProfile.objects.filter(active=2,organization_type=2)

    if request.method == 'POST':
        try:
            instance = get_object_or_404(Project, slug=slug)
            form = ProjectForm(request.POST,request.FILES or None, instance=instance)
        except:
            form = ProjectForm(request.POST,request.FILES)
            instance = ''
        project_name = Project.objects.all()
        # for j in project_name:
        #     if j.name == request.POST.get('name'):
        #         messages.error(request, 'Project Name already Exist')
        #         return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if form.is_valid():
            obj = form.save(commit=False)
            obj.content_type = ContentType.objects.get(model="Program")
            obj.object_id = 0
            try:
                obj.created_by = UserProfile.objects.get(id=user_id)
            except:
                pass
            if not instance:
                obj.slug = unique_slug_generator(obj)
            obj.save()
            form.save_m2m()
            activity_del = PrimaryWork.objects.filter(object_id=obj.id,content_type=ContentType.objects.get(model="project")).delete()
            try:
                activity_count = int(request.POST.get('activity_count'))
                i=1
                for i in range(activity_count):
                    act = 'activity['+str(i+1)+']'
                    dur = 'duration['+str(i+1)+']'
                    activity = request.POST.get(act)
                    duration = request.POST.get(dur)
                    create_activity = PrimaryWork.objects.create(name=activity,types=0,number=i+1,\
                                        activity_duration=duration,content_type=ContentType.objects.get(model="project"),\
                                        object_id=obj.id)
            except:
                pass
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

def unique_slug_generator(instance, new_slug=None):
    """
    This is for a Django project and it assumes your instance 
    has a model with a slug field and a title character (char) field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.name)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
                    slug=slug,
                    randstr=random_string_generator(size=4)
                )
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug


def project_list(request):
    user_id = request.session.get('user_id')
    user_obj = UserProfile.objects.get(user_reference_id = user_id )
    if user_obj.is_admin_user == True:
        obj_list = Project.objects.filter()
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

def project_detail(request):
    slug =  request.GET.get('slug')
    obj = Project.objects.get_or_none(slug=slug)
    activity = PrimaryWork.objects.filter(content_type=ContentType.objects.get(model="project"),object_id=obj.id)
    return render(request,'project/comany-profile.html',locals())


def project_mapping(request):
    form = ProjectMappingForm()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/dashboard/')
    return render(request,'project/project_mapping.html',locals())

def upload_attachment(request):
    slug =  request.GET.get('slug')
    model =  request.GET.get('model')
    key = int(request.GET.get('key'))
    project_obj = Project.objects.get(slug=slug)
    if key==1:
        #key 1 for Document upload
        form = AttachmentForm()
    else:
        form = ImageUpload()
    if request.method == 'POST':
        if key==1:
            form = AttachmentForm(request.POST, request.FILES)
        else:
            form = ImageUpload(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.content_type=ContentType.objects.get(model=model)
            obj.object_id=project_obj.id
            if key==1:
                obj.attachment_type=2
            else:
                obj.attachment_type=1
            obj.save()
        try:
            keys = request.POST.get('keywords').split(',')
            key_model = 'Attachment'
            keywords = add_keywords(keys,obj,key_model,0)
        except:
            pass
        # url = 'upload/list/?slug=%s&model=Project' %slug
        return HttpResponseRedirect('/upload/list/?slug=%s&model=%s' %(slug,model))

    return render(request,'attachment/doc_upload.html',locals())

def edit_attachment(request):
    ids = request.GET.get('id')
    obj_id =  request.GET.get('obj_id')
    slug = Project.objects.get(id=obj_id).slug
    model =  request.GET.get('model')
    obj = Attachment.objects.get(id=ids)
    if obj.attachment_type==2:
        #key 1 for Document upload
        form = AttachmentForm(instance = obj)
        key=1
    else:
        form = ImageUpload(instance = obj)
        key=2
    if request.method == 'POST':
        instance = get_object_or_404(Attachment, id=ids)
        if key==1:
            form = AttachmentForm(request.POST, request.FILES or None, instance=instance)
        else:
            form = ImageUpload(request.POST, request.FILES or None, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
        try:
            keys = request.POST.get('keywords').split(',')
            attach_model = 'Attachment'
            keywords = add_keywords(keys,obj,attach_model,1)
        except:
            pass
            return HttpResponseRedirect('/upload/list/?slug=%s&model=%s' %(slug,model))
    return render(request,'attachment/doc_upload.html',locals())

def add_keywords(keys,obj,model,edit):
    if edit==1:
        delete = FileKeywords.objects.filter(content_type=ContentType.objects.get(model=model),object_id=obj.id)
    key_list = Keywords.objects.filter(active=2)
    for i in keys:
        key_obj = Keywords.objects.get_or_none(name__iexact=i.strip())
        if key_obj:
            if not key_obj.id in key_list.values_list('name',flat=True):
                key_obj = FileKeywords.objects.create(key=key_obj,content_type=ContentType.objects.get(model=model),object_id=obj.id)
        else:
            key_object = Keywords.objects.create(name=i.strip())
            key_obj = FileKeywords.objects.create(key=key_object,content_type=ContentType.objects.get(model=model),object_id=obj.id )

def budget_tranche(request):
    form = TrancheForm()
    slug =  request.GET.get('slug')
    user_id = request.session.get('user_id')
    project = Project.objects.get_or_none(slug=slug)
    # form.fields["project"].queryset = Project.objects.filter(created_by__id=user_id)
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
    user_id = request.session.get('user_id')
    tranche_list = Tranche.objects.filter(project__slug=slug)
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
        # return HttpResponseRedirect("/masterdata/component-question/?id=%s" % key)
    return render(request,'project/add_key_parameter.html',locals())

def upload_parameter(request):
    ids =  request.GET.get('id')
    key =  request.GET.get('key')
    parameter = ProjectParameter.objects.get(id=ids)
    key_parameter = ProjectParameter.objects.filter(parent=parameter)
    key_parameter_list = [i.id for i in key_parameter]
    key_parameter_value = ProjectParameterValue.objects.filter(keyparameter__in=key_parameter_list)
    existing_month = [k.start_date.month for k in key_parameter_value]
    month = ['January','February','March','April','May','June','July','August','September','October','November','December']
    month_id = [1,2,3,4,5,6,7,8,9,10,11,12]
    month_zip = zip(month,month_id)
    if request.method == 'POST':
        month = int(request.POST.get('month'))
        now = datetime.datetime.now()
        date = str(now.year)+'-'+str(month)+'-'+'1'
        days = monthrange(now.year, month)[1]
        end_date = str(now.year)+'-'+str(month)+'-'+str(days)
        submit_date = str(now.year)+'-'+str(now.month)+'-'+str(now.day)
        if key_parameter.exists():
            total_count = []
            for i in key_parameter:
                value = 'value['+str(i.id)+']'
                obj = ProjectParameterValue.objects.create(keyparameter=i,parameter_value=request.POST.get(value),\
                                start_date=date,end_date=end_date,submit_date=submit_date)
        else:
            obj = ProjectParameterValue.objects.create(keyparameter=parameter,parameter_value=request.POST.get('value'),\
                                start_date=date,end_date=end_date,submit_date=submit_date)
        return HttpResponseRedirect('/project/parameter/manage/?slug=%s&key=2' %parameter.project.slug)
    return render(request,'project/key_parameter.html',locals())

def manage_parameter(request):
    slug =  request.GET.get('slug')
    parameter = ProjectParameter.objects.filter(project__slug=slug,parent=None)
    project_name = Project.objects.get(slug=slug).name
    return render(request,'project/parameter_list.html',locals())


# def manage_parameter_values(request):
#     ids =  request.GET.get('id')
#     parameter1 = ProjectParameter.objects.get(id=ids)
#     # key_parameter = ProjectParameter.objects.filter(parent=parameter)

#     parameter = ProjectParameterValue.objects.filter(keyparameter__id=ids)
#     import ipdb;ipdb.set_trace()
#     coloumn = []
#     coloumn.append('Month')

#     for i in parameter:
#         para_type = i.keyparameter.parameter_type
#         if para_type == 'PIN' or para_type == 'PIP':
#             key_parameter = ProjectParameterValue.objects.filter(keyparameter__parent=parameter1)
#             coloumn.append(i.keyparameter.name)
#         else:
#             coloumn.append(i.keyparameter.name)
#             key_parameter=''
#     import ipdb;ipdb.set_trace()
#     return render(request,'project/parameter_value_list.html',locals())

def manage_parameter_values(request):
    ids =  request.GET.get('id')
    parameter = ProjectParameter.objects.get(id=ids)
    parameter_count = ProjectParameter.objects.filter(parent=parameter).count() + 1
    if parameter.parameter_type == 'NUM' or parameter.parameter_type == 'CUR' or parameter.parameter_type == 'PER':
        ff = ProjectParameterValue.objects.filter(keyparameter=parameter)
    else:
        child_parameter = ProjectParameterValue.objects.filter(keyparameter__parent=parameter).order_by('-submit_date')
        # child_parameter = ProjectParameterValue.objects.filter(keyparameter__parent=para)

    name_range = range(1,parameter_count)
    values_list = child_parameter.values_list('parameter_value',flat=True)
    values = aggregate_project_parameters(parameter,child_parameter)
    return render(request,'project/parameter_value_list.html',locals())

def aggregate_project_parameters(param, values):
    ret={}
    aggr=0
    if param.aggregation_function=='ADD':
        for val in values:
            aggr+= int(val.parameter_value)
    elif param.aggregation_function=='AVG' :
        cnt=0
        for val in values:
            cnt+=1
            aggr += int(val.parameter_value)
        aggr=aggr/cnt
    elif param.aggregation_function == "WAV":
        paggr=0
        for val in values:

            parent=ProjectParameterValue.objects.filter(keyparameter_id=param.parent_id,period_id=val.period_id)
            aggr+=int(val.parameter_value)*int(parent.parameter_value)
            paggr+=int(parent.parameter_value)
        aggr=aggr/paggr
    elif param.aggregation_function == "WAP":
        paggr=0
        for val in values:

            parent=ProjectParameterValue.objects.filter(keyparameter_id=param.parent_id,period_id=val.period_id)
            aggr+=int(val.parameter_value)*int(parent.parameter_value)
            paggr+=int(parent.parameter_value)
        aggr=aggr/paggr

    ret['name']=param.name
    ret['parameter_type']= param.parameter_type
    ret['instructions'] = param.instructions
    ret['aggregate_value'] = aggr
    ret['parent_name'] = None if param.parent is None else param.parent.name
    return ret

def project_total_budget(slug):
# to display the total budget ,disbursed,utilized percent in project summary page
    try:
        project = Project.objects.get(slug=slug)
        budget = project.project_budget_details()
        planned_cost = float(budget.get('planned_cost') or 0)/10000000
        utilized_cost = float(budget.get('utilized_cost') or 0)/10000000
        disbursed_budget = float(budget.get('disbursed_cost') or 0)/10000000
        total_percent = 100
        disbursed_percent = int((disbursed_budget/planned_cost)*100)
        utilized_percent = int((utilized_cost/planned_cost)*100)
    except:
        planned_cost= utilized_cost=disbursed_budget=total_percent= disbursed_percent=utilized_percent =0

    budget =  {'total':planned_cost,'disbursed':disbursed_budget,'utilized':utilized_cost,
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
    image_url = PMU_URL
    slug =  request.GET.get('slug')
    user_id = request.session.get('user_id')
    user_obj = UserProfile.objects.get(user_reference_id = user_id)
    obj = Project.objects.get_or_none(slug = slug)
    projectuserlist = ProjectUserRoleRelationship.objects.filter(project=obj)
    tasks = total_tasks_completed(obj.slug)
    updates_list = updates(Project.objects.filter(slug=slug))
    budget = project_total_budget(obj.slug)
    timeline = timeline_listing(obj)
    project_funders = ProjectFunderRelation.objects.get_or_none(project = obj)
# key paramter function
    master_obj = []
    master_obj_pin=[]
    master_obj_pip=[]
    parameter = ProjectParameter.objects.filter(project=obj,parent=None)
    parameter_count = parameter.count()
    for i in parameter:
        if i.parameter_type == 'NUM' or i.parameter_type == 'PER' or i.parameter_type == 'CUR':
            parameter1 = ProjectParameter.objects.filter(project=obj,parent=None).values_list('id',flat=True)
            parent_paremeter = ProjectParameterValue.objects.filter(keyparameter__in=parameter1)
        elif i.parameter_type == 'PIN':
            child_parameter_pin = ProjectParameterValue.objects.filter(keyparameter__parent=i.id,keyparameter__parameter_type='PIN')
            if child_parameter_pin.exists():
                master_obj_pin = child_parameter_pin
                chart_name_pin = child_parameter_pin[0].keyparameter.parent.name
        elif i.parameter_type == 'PIP':
            child_parameter_pip = ProjectParameterValue.objects.filter(keyparameter__parent=i.id,keyparameter__parameter_type='PIP')
            if child_parameter_pip.exists():
                master_obj_pip = child_parameter_pip
                chart_name_pip = child_parameter_pip[0].keyparameter.parent.name
            pass
    import json
    list1=[]
    aa = ProjectParameterValue.objects.filter(keyparameter__project=obj,keyparameter__parent=None)
    for i in aa:
        if i.keyparameter.parameter_type=='PIN' or i.keyparameter.parameter_type=='PIP':
            pin = ProjectParameterValue.objects.filter(keyparameter__parameter_type='PIN',keyparameter__project=obj)
        # for p in pin:
    pin = ProjectParameterValue.objects.filter(keyparameter__parameter_type='PIN',keyparameter__project=obj)
    tst = ProjectParameter.objects.filter(project=obj,parent=None)
    colors=['#5485BC', '#AA8C30', '#5C9384', '#981A37', '#FCB319','#86A033', '#614931', '#00526F', '#594266', '#cb6828', '#aaaaab', '#a89375']
    counter =0
    master_l = []
    name_list = []
    para_name = {}
    pin_title_name = []
    pip_title_name = []
    for i in tst:
        if i.parameter_type=='NUM' or i.parameter_type=='PER' or i.parameter_type=='CUR':
            pass
            ttt=[]
        elif i.parameter_type=='PIN' or i.parameter_type=='PIP':
            
            ttt = []
            fds = ProjectParameterValue.objects.filter(keyparameter__parent=i)
            for j in fds:
                name = str(j.keyparameter.name)
                value = float(j.parameter_value)
                color = colors[counter]
                counter+=1
                pin_title_name
                ttt.append({'name': name,'y':value,'color':color})
        if ttt:
            if i.parameter_type in para_name:
                para_name[i.parameter_type].append(ttt)
            else:
                para_name.setdefault(i.parameter_type,[])
                para_name[i.parameter_type].append(ttt)
            name_list.append(str(i.name))
        if i.parameter_type == 'PIN':
            pin_title_name.append(str(i.name))
        if i.parameter_type == 'PIP':
            pip_title_name.append(str(i.name))
    # data_list_pin=[]
    # data_list_pip=[]
    # counter = 0
    # for k in master_obj_pin:
    #     name = str(k.keyparameter.name)
    #     value = float(k.parameter_value)
    #     color = colors[counter]
    #     counter+=1
    #     data_list_pin.append({'name': name,'y':value,'color':color})
    # for k in master_obj_pip:
    #     name = str(k.keyparameter.name)
    #     value = float(k.parameter_value)
    #     color = colors[counter]
    #     counter+=1
    #     data_list_pip.append({'name': name,'y':value,'color':color})
    # data_pip = json.dumps(data_list_pip)
    # data_pin = json.dumps(data_list_pin)
    master_sh = para_name
    
    master_sh_len = {key:len(values) for key,values in master_sh.items()}
    master_pin = map(lambda x: "Batch_size_" + str(x), range(master_sh_len.get('PIN',0)))
    master_pip = map(lambda x: "Beneficary_distribution_"+ str(x), range(master_sh_len.get('PIP',0)))
    data = {'project_id':int(obj.id)}
    rdd = requests.get(PMU_URL +'/managing/gantt-chart-data/', data=data)
    taskdict = ast.literal_eval(json.dumps(rdd.content))
    print taskdict
    return render(request,'project/project-summary.html',locals())
