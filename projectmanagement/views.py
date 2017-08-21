from django.shortcuts import render
from projectmanagement.models import *
from projectmanagement.forms import *
from django.http import HttpResponseRedirect
from django.shortcuts import get_list_or_404, get_object_or_404
from django.contrib.contenttypes.models import ContentType
# Create your views here.

def create_project(request):
    # import ipdb; ipdb.set_trace()
    try:
        ids =  request.GET.get('id')
        obj = Project.objects.get(id=ids)
        form = ProjectForm(instance = obj)
        activity_view = PrimaryWork.objects.filter(object_id=obj.id,content_type=ContentType.objects.get(model="project"))
        mapping_view = ProjectFunderRelation.objects.get(project=obj)
    except:
        form = ProjectForm()
    funder_user = UserProfile.objects.filter(active=2)
    if request.method == 'POST':
        import ipdb; ipdb.set_trace()
        try:
            instance = get_object_or_404(Project, id=ids)
            form = ProjectForm(request.POST,request.FILES or None, instance=instance)
        except:
            form = ProjectForm(request.POST,request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            # form.save_m2m()
            obj.content_type = ContentType.objects.get(model="Program")
            obj.object_id = 23
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
    ids =  request.GET.get('id')
    obj = Project.objects.get(id=ids)
    return render(request,'project/project_details.html',locals())

def project_mapping(request):
    form = ProjectMappingForm()
    if request.method == 'POST':
        import ipdb; ipdb.set_trace()
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/dashboard/')
    return render(request,'project/project_mapping.html',locals())

def upload_attachment(model,obj_id,desc,attach_file):
    attach = Attachment.objects.create(attachment_file=attach_file,name=desc,\
                    content_type=ContentType.objects.get(model=model),object_id=obj_id)

# def upload_attachment_type(model,obj_id,desc,attach_file,attach_type):
#     attach = Attachment.objects.create(attachment_file=attach_file,name=desc,\
#                     content_type=ContentType.objects.get(model=model),object_id=obj_id,attachment_type=attach_type)