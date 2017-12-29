from django.shortcuts import render
from media.models import *
from budgetmanagement.models import Tranche
from django.http import HttpResponseRedirect
from django.http import HttpResponse
import json
from django.shortcuts import get_list_or_404, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from pmu.settings import PMU_URL
from projectmanagement.models import Project,Boundary
from media.forms import AttachmentForm,ImageUpload
from projectmanagement.common_method import unique_slug_generator,add_keywords

def list_document(request):
    # this function will list documents of project
    slug =  request.GET.get('slug')
    model = eval(request.GET.get('model'))
    try:
        obj = model.objects.get(slug=slug)
    except:
        ids = request.GET.get('id')
        obj = model.objects.get(id=ids)
    attachment = Attachment.objects.filter(active=2,object_id=obj.id,content_type=ContentType.objects.get(model=request.GET.get('model'))).order_by('-created')
    image = PMU_URL
    key = request.GET.get('key')
    user_id = request.session.get('user_id')
    user = UserProfile.objects.get_or_none(user_reference_id = user_id)
    from taskmanagement.views import get_assigned_users
    status = get_assigned_users(user,obj)
    projectobj = obj
    return render(request,'attachment/listing.html',locals())
	
def timeline_upload(request):
    # this function is to upload images in timeline (for project summary page)
    slug = request.GET.get('slug')
    user_id = request.session.get('user_id')
    user = UserProfile.objects.get(user_reference_id = user_id)
    try:
        project = Project.objects.get(slug = request.POST.get('slug'))
    except:
        project = Project.objects.get(slug=slug)
    form = ImageUpload()
    if request.method=='POST':
        form=ImageUpload(request.POST,request.FILES)
        if form.is_valid():
            f=form.save()
            f.attachment_type = 1
            f.created_by = user
            f.content_type = ContentType.objects.get(model=('project'))
            f.object_id = project.id
            f.timeline_progress = True
            f.save()
            return HttpResponseRedirect('/project/summary/?slug='+project.slug)
        else :
            return HttpResponseRedirect('/project/summary/?slug='+project.slug)
    else:
        form=ImageUpload()
    timeline = 1
    return render(request,'taskmanagement/forms.html',locals())

def upload_attachment(request):
    '''
    This function is to upload Image/Document 
    '''
    user_id = request.session.get('user_id')
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
            obj.name = request.POST.get('name')
            obj.description = request.POST.get('description')
            obj.content_type=ContentType.objects.get(model=model)
            obj.object_id=project_obj.id
            obj.created_by = UserProfile.objects.get_or_none(user_reference_id=user_id)
            if key==1:
                obj.attachment_type=2
            else:
                obj.attachment_type=1
                obj.timeline_progress = False
            obj.save()
        try:
            keys = request.POST.get('keywords').split(',')
            key_model = 'Attachment'
            keywords = add_keywords(keys,obj,key_model,0)
        except:
            pass
        return HttpResponseRedirect('/upload/list/?slug=%s&model=%s' %(slug,model))

    return render(request,'attachment/doc_upload.html',locals())

def edit_attachment(request):
    '''
    This function is to edit Image/Document
    '''
    ids = request.GET.get('id')
    obj_id =  request.GET.get('obj_id')
    if request.method == 'GET':
        slug = Project.objects.get_or_none(id=obj_id).slug
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
        return HttpResponseRedirect('/upload/list/?slug=%s&model=%s' %(request.GET.get('slug'),model))
    return render(request,'attachment/doc_upload.html',locals())

def city_list(request):
    results ={}
    if request.is_ajax():
        ids =  request.GET.get('state_id')
        city_obj = Boundary.objects.filter(boundary_level=3,parent__id=ids).order_by('name').values('id','name')
        results['res']=list(city_obj)
        return HttpResponse(json.dumps(results), content_type='application/json')
