from django.shortcuts import render
import datetime
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
    funder_user = UserProfile.objects.filter(active=2,organization_type=2)
    partner = UserProfile.objects.filter(active=2,organization_type=1)

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
            try:
                obj.created_by = UserProfile.objects.get(id=user_id)
            except:
                pass
            if not instance:
                obj.slug = obj.name.replace(' ','-')
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
                mapping = ProjectFunderRelation.objects.create(project=obj,funder=funder,\
                        implementation_partner=implementation_partner,total_budget=request.POST.get('total_budget'))
            return HttpResponseRedirect('/project/list/')
    return render(request,'project/project_edit.html',locals())

def project_list(request):
    user_id = request.session.get('user_id')
    user_obj = UserProfile.objects.get(user_reference_id = user_id )
    obj_list = Project.objects.filter(created_by = user_obj)
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
            model = 'Attachment'
            keywords = add_keywords(keys,obj,model,0)
        except:
            pass
        # url = 'upload/list/?slug=%s&model=Project' %slug
        return HttpResponseRedirect('/project/list/')

    return render(request,'attachment/doc_upload.html',locals())

def edit_attachment(request):
    ids = request.GET.get('id')
    obj_id =  request.GET.get('obj_id')
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
            model = 'Attachment'
            keywords = add_keywords(keys,obj,model,1)
        except:
            pass
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
    user_id = request.session.get('user_id')
    form.fields["project"].queryset = Project.objects.filter(created_by__id=user_id)
    form.fields["recommended_by"].queryset = UserProfile.objects.filter(is_admin_user=True)
    if request.method == 'POST':
        form = TrancheForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            return HttpResponseRedirect('/dashboard/')
    return render(request,'budget/tranche.html',locals())

def tranche_list(request):
    user_id = request.session.get('user_id')
    tranche_list = Tranche.objects.filter()
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
    if request.method == 'POST':
        slug =  request.GET.get('slug')
        project = Project.objects.get(slug=slug)
        parameter_type = request.POST.get('para_type')
        name = request.POST.get('name')
        instruction = request.POST.get('instruction')
        name_count = int(request.POST.get('name_count'))
        agg_type = request.POST.get('agg_type')
        parent_obj = ProjectParameter.objects.create(parameter_type=parameter_type,\
                                project=project,aggregation_function=agg_type,name = name)
        if name_count != 0:
            for i in range(name_count):
                name = 'name['+str(i+1)+']'
                obj = ProjectParameter.objects.create(parameter_type=parameter_type,project=project,\
                        name=request.POST.get(name),parent=parent_obj,aggregation_function=request.POST.get('agg_type'))
        return HttpResponseRedirect('/project/parameter/manage/?slug=%s' %slug)
        # return HttpResponseRedirect("/masterdata/component-question/?id=%s" % key)
    return render(request,'project/add_key_parameter.html',locals())

def upload_parameter(request):
    ids =  request.GET.get('id')
    parameter = ProjectParameter.objects.get(id=ids)
    key_parameter = ProjectParameter.objects.filter(parent=parameter)
    if request.method == 'POST':
        month = int(request.POST.get('month'))
        now = datetime.datetime.now()
        date = str(now.year)+'-'+str(month)+'-'+'1'
        days = monthrange(now.year, month)[1]
        end_date = str(now.year)+'-'+str(month)+'-'+str(days)
        submit_date = str(now.year)+'-'+str(now.month)+'-'+str(now.day)
        if key_parameter.exists():
            for i in key_parameter:
                value = 'value['+str(i.id)+']'
                obj = ProjectParameterValue.objects.create(keyparameter=i,parameter_value=request.POST.get(value),\
                                start_date=date,end_date=end_date,submit_date=submit_date)
        else:
            obj = ProjectParameterValue.objects.create(keyparameter=parameter,parameter_value=request.POST.get('value'),\
                                start_date=date,end_date=end_date,submit_date=submit_date)
        return HttpResponseRedirect('/project/parameter/manage/?slug=%s' %parameter.project.slug)
    return render(request,'project/key_parameter.html',locals())

def manage_parameter(request):
    slug =  request.GET.get('slug')
    parameter = ProjectParameter.objects.filter(project__slug=slug,parent=None)
    return render(request,'project/parameter_list.html',locals())


def manage_parameter_values(request):
    ids =  request.GET.get('id')
    parameter1 = ProjectParameter.objects.get(id=ids)
    # key_parameter = ProjectParameter.objects.filter(parent=parameter)

    parameter = ProjectParameterValue.objects.get_or_none(keyparameter__id=ids)
    import ipdb;ipdb.set_trace()
    key_parameter = ProjectParameterValue.objects.filter(keyparameter__parent=parameter1)
    return render(request,'project/parameter_value_list.html',locals())