from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from pmu.settings import BASE_DIR
from taskmanagement.models import *
from taskmanagement.forms import ActivityForm,TaskForm,MilestoneForm
from projectmanagement.models import Project,UserProfile
# Create your views here.

def listing(request,model_name):
#    model = ContentType.objects.get(model__iexact = model_name)
    obj_list = eval(model_name).objects.all().order_by('-id')
    return render(request,'listing.html',locals())
    
def add_taskmanagement(request,model_name,m_form):
    user_id = request.session.get('_auth_user_id')
    user = UserProfile.objects.get(user_reference_id = user_id)
    form=eval(m_form)
    if request.method=='POST':
        form=form(user_id,request.POST,request.FILES)
        if model_name == 'Activity' or model_name == 'Task':
            form.assigned_to = UserProfile.objects.get(user_reference_id = request.POST['assigned_to'])
        if form.is_valid():
            f=form.save() 
            if model_name == 'Activity' or model_name == 'Task':
                f.slug = f.name.replace(' ','-')
                f.created_by = user
                f.save()
                return HttpResponseRedirect('/manage-task/'+model_name+'/listing/')
    else:
        form=form(user_id)
    return render(request,'taskmanagement/forms.html',locals())
    
def edit_taskmanagement(request,model_name,m_form,slug):
    user_id = request.session.get('_auth_user_id')
    user = UserProfile.objects.get(user_reference_id = user_id)
    form=eval(m_form)
    m=eval(model_name).objects.get(slug = slug)
    if request.method == 'POST':
        form=form(user_id,request.POST,request.FILES,instance=m)
        if model_name == 'Activity' or model_name == 'Task':
            form.assigned_to = UserProfile.objects.get(user_reference_id = request.POST['assigned_to'])
        if form.is_valid():
            f=form.save()
            if model_name == 'Activity' or model_name == 'Task':
                f.slug = f.name.replace(' ','-')
                f.created_by = user
                f.save()
                return HttpResponseRedirect('/manage-task/'+model_name+'/listing/')
    else:
        form=form(user_id,instance=m)
    return render(request,'taskmanagement/forms.html',locals())

def active_change(request,model_name):
    ids = request.GET.get('id')
    status = request.GET.get('status')
    url=request.META.get('HTTP_REFERER')
    model = ContentType.objects.get(model = model_name)
    obj = model.model_class().objects.get(id=int(ids))
    if  obj.active ==2:
        obj.active=0
        obj.save()
        msg = 'deactivate'
    elif obj.active==0:
        obj.active=2
        obj.save()
        msg ='active'
    return HttpResponseRedirect(url)
    
from django.http import JsonResponse
def task_start_date(request):
    start_date = ''
    ids = request.GET.get('id')
    url=request.META.get('HTTP_REFERER')
    obj = None
    try:
        obj = Activity.objects.get(active=2,id= int(ids),activity_type = 1)
        project = Project.objects.get(id = obj.object_id)
        start_date = project.start_date.strftime('%Y-%m-%d')
    except:
        obj = None
    return JsonResponse({"project_start_date":start_date})
    
