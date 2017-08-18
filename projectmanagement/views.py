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
    except:
        form = ProjectForm()

    if request.method == 'POST':
        try:
            instance = get_object_or_404(Project, id=ids)
            form = ProjectForm(request.POST,request.FILES or None, instance=instance)
        except:
            form = ProjectForm(request.POST,request.FILES)

        activity_count = int(request.POST.get('activity_count'))
        i=1
        if form.is_valid():
            obj = form.save(commit=False)
            # form.save_m2m()
            obj.content_type = ContentType.objects.get(model="Program")
            obj.object_id = 23
            obj.save()
            form.save_m2m()
            activity_del = PrimaryWork.objects.filter(object_id=obj.id,content_type=ContentType.objects.get(model="project")).delete()
            for i in range(activity_count):
                act = 'activity['+str(i+1)+']'
                dur = 'duration['+str(i+1)+']'
                activity = request.POST.get(act)
                duration = request.POST.get(dur)
                create_activity = PrimaryWork.objects.create(name=activity,types=0,number=i+1,\
                                    activity_duration=duration,content_type=ContentType.objects.get(model="project"),\
                                    object_id=obj.id)
            return HttpResponseRedirect('/project/list/')
    return render(request,'project_edit.html',locals())

def project_list(request):
    obj_list = Project.objects.all()
    return render(request,'listing.html',locals())

def project_detail(request):
    ids =  request.GET.get('id')
    obj = Project.objects.get(id=ids)
    return render(request,'project_details.html',locals())