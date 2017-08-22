from django.shortcuts import render
from projectmanagement.models import *
from projectmanagement.forms import *
from budgetmanagement.forms import TrancheForm
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
        activity_view = PrimaryWork.objects.filter(object_id=obj.id,content_type=ContentType.objects.get(model="project"))
        mapping_view = ProjectFunderRelation.objects.get(project=obj)
    except:
        form = ProjectForm()
    funder_user = UserProfile.objects.filter(active=2)
    if request.method == 'POST':
        import ipdb; ipdb.set_trace()
        try:
            instance = get_object_or_404(Project, slug=slug)
            form = ProjectForm(request.POST,request.FILES or None, instance=instance)
        except:
            form = ProjectForm(request.POST,request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.content_type = ContentType.objects.get(model="Program")
            obj.object_id = 0
            try:
                obj.created_by = UserProfile.objects.get(id=user_id)
            except:
                pass
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
    obj_list = Project.objects.all()
    return render(request,'project/listing.html',locals())

def project_detail(request):
    slug =  request.GET.get('slug')
    obj = Project.objects.get(slug=slug)
    return render(request,'project/project_details.html',locals())

def project_mapping(request):
    form = ProjectMappingForm()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/dashboard/')
    return render(request,'project/project_mapping.html',locals())

def upload_attachment(request):
    obj_id =  request.GET.get('obj_id')
    model =  request.GET.get('model')
    key = int(request.GET.get('key'))
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
            obj.object_id=obj_id
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
                obj = FileKeywords.objects.create(key=key_obj,content_type=ContentType.objects.get(model=model),object_id=obj.id)
        else:
            key_object = Keywords.objects.create(name=i.strip())
            obj = FileKeywords.objects.create(key=key_object,content_type=ContentType.objects.get(model=model),object_id=obj.id )

def budget_tranche(request):
    form = TrancheForm()
    if request.method == 'POST':
        form = TrancheForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            return HttpResponseRedirect('/dashboard/')
    return render(request,'budget/tranche.html',locals())