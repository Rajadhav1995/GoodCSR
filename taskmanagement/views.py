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
from media.models import Attachment
# Create your views here.

def listing(request,model_name):
#    model = ContentType.objects.get(model__iexact = model_name)
    obj_list = eval(model_name).objects.all().order_by('-id')
    return render(request,'listing.html',locals())

def add_taskmanagement(request,model_name,m_form):
    if model_name == 'Activity':
        try:
            project_id = Project.objects.get(slug = request.GET.get('slug')).id
        except:
            project_id = Project.objects.get(id = request.POST.get('project')).id
    else :
        project_id = None
    user_id = request.session.get('user_id')
    user = UserProfile.objects.get(user_reference_id = user_id)
    form=eval(m_form)
    if request.method=='POST':
        form=form(user_id,project_id,request.POST,request.FILES)
        if form.is_valid():
            f=form.save()
            if model_name == 'Activity' or model_name == 'Task':
                f.slug = f.name.replace(' ','-')
                f.created_by = user
                f.save()
                return HttpResponseRedirect('/managing/'+model_name+'/listing/')
            else :
                return HttpResponseRedirect('/managing/'+model_name+'/listing/')
    else:
        form=form(user_id,project_id)
    return render(request,'taskmanagement/forms.html',locals())

def edit_taskmanagement(request,model_name,m_form,slug):
    user_id = request.session.get('user_id')
    user = UserProfile.objects.get(user_reference_id = user_id)
    form=eval(m_form)
    if model_name == 'Milestone':
        m = eval(model_name).objects.get(id = int(slug))
    else :
        m=eval(model_name).objects.get(slug = slug)
    project_id = m.project.id if model_name == 'Activity' else None
    if request.method == 'POST':
        form=form(user_id,project_id,request.POST,request.FILES,instance=m)
        if form.is_valid():
            f=form.save()
            if model_name == 'Activity' or model_name == 'Task':
                f.slug = f.name.replace(' ','-')
                f.created_by = user
                f.save()
                return HttpResponseRedirect('/managing/'+model_name+'/listing/')
            else:
                return HttpResponseRedirect('/managing/'+model_name+'/listing/')
    else:
        form=form(user_id,project_id,instance=m)
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
def task_dependencies(request):
    start_date = ''
    tasks = None
    ids = request.GET.get('id')
    url=request.META.get('HTTP_REFERER')
    obj = None
    try:
        tasks = Task.objects.filter(active=2,activity = int(ids))
        obj = Activity.objects.get(active=2,id= int(ids),activity_type = 1)
        project = Project.objects.get(id = obj.project.id)
        start_date = project.start_date.strftime('%Y-%m-%d')
    except:
        obj = None
    if not tasks:
        tasks = []
    else:
        tasks = [{'id':i.id,'name':i.name} for i in tasks if i.is_dependent() != True]
    return JsonResponse({"project_start_date":start_date,'tasks_dependency': tasks})

# to compute start date of the tasks dependent
def task_auto_computation_date(request):
    ids = request.GET.get('id')
    url=request.META.get('HTTP_REFERER')
    obj = None
    try:
        task = Task.objects.get(active=2,id= int(ids))
        end_date = task.end_date.strftime('%Y-%m-%d')
    except:
        obj = None
        end_date = ''
    return JsonResponse({"computation_date":end_date})

def milestone_overdue(request):
    task_ids = request.GET.get('id[]')
    url=request.META.get('HTTP_REFERER')
    tasks_obj = Task.objects.filter(id__in = task_ids).values_list('end_date',flat = True)
    milestone_overdue = max(tasks_obj).strftime('%Y-%m-%d')
    return JsonResponse({"milestone_overdue_date":milestone_overdue})

from datetime import datetime
#slug = Project slug and this is to display in project summary dashboard
def total_tasks_completed(slug):
    total_tasks = completed_tasks=total_milestones = 0
    milestones = []
    project = Project.objects.get(slug = slug)
    activity = Activity.objects.filter(project=project)
    for act in activity:
        tasks = Task.objects.filter(activity = act)
        total_tasks = len(tasks) + total_tasks
        for t in tasks:
            if t.end_date.strftime('%Y-%m-%d') <= datetime.now().strftime('%Y-%m-%d'):
                completed_tasks = completed_tasks + 1
            miles_obj = Milestone.objects.get_or_none(task = t)
            if miles_obj not in milestones:
                milestones.append(miles_obj)
    if completed_tasks != 0:
        percent =int((float(completed_tasks) / float(total_tasks))*100)
    else:
        percent = 0
    print milestones
    if milestones:
        total_milestones = len(milestones)
    return project,total_tasks,completed_tasks,milestones,total_milestones,percent


def my_task_updates(obj_list):
#updates of the task
    try:
        task_obj = Task.objects.get(id = int(task_id))
        attachment = Attachment.objects.filter(active = 2,content_type = ContentType.objects.get_for_model(task_obj),object_id = task.id).order_by('created_by')
    except:
        attachment = []
    return attachment

def my_task_details(task_id):
    try:
        task = Task.objects.get(id = int(task_id))
    except:
        task = []
    return task
   
def my_tasks_listing():
    tasks = Task.objects.filter(active=2).order_by('-createdby')
    return tasks
    
def updates(obj_list):
    formats = '%H:%M %p'
    uploads = []
    task_completed = {}
    completed_tasks = []
    task_uploads = {}
    for project in obj_list:
        project = Project.objects.get(id = int(project.id))
        activity = Activity.objects.filter(project=project)
        for act in activity:
            task_list = Task.objects.filter(activity = act)
            for task in task_list:
                attach_list = Attachment.objects.filter(active=2,content_type = ContentType.objects.get_for_model(task),object_id = task.id).order_by('created')
                if attach_list:
                    for attach in attach_list:
                        task_uploads={'project_name':project.name,'task_name':task.name,'attach':attach.description,
                        'user_name':attach.created_by.email,'time':attach.created.time(),'date':attach.created.date(),'task_status':task.history.latest()}
                        uploads.append(task_uploads)
                if task.status == 2 and task.history.latest():
                    task_uploads={'project_name':project.name,'task_name':task.name,'attach':'',
                        'user_name':task.created_by.email,'time':task.modified.time(),'date':task.modified.date(),'task_status':task.history.latest()}
                    uploads.append(task_uploads)
    return uploads
        
def corp_task_completion_chart(obj_list):
#    progress={}
    task_progress =[] 
    total_percent=[]  
    if obj_list:
        for project in obj_list:
            total_tasks = project.total_tasks()
            tasks_completed_count = project.tasks_completed()
            percentage = int((float(tasks_completed_count) / float(total_tasks))*100)
            remaining_percent = 100 - percentage
            total_percent.append(str(percentage))
            progress = project.name+ ' ' + str(percentage)+'%'
            task_progress.append(progress)
    return task_progress
