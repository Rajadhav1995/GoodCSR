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
from projectmanagement.models import Project,UserProfile,ProjectFunderRelation
from media.models import Attachment
from budgetmanagement.models import *
from userprofile.models import ProjectUserRoleRelationship

# Create your views here.

#def listing(request,model_name):
##    model = ContentType.objects.get(model__iexact = model_name)
#    obj_list = eval(model_name).objects.all().order_by('-id')
#    if model_name == 'Activity':
#        project = Project.object.get_or_none(slug = request.GET.get('slug'))
#        obj_list = eval(model_name).objects.filter(project = project).order_by('-id')
#    return render(request,'listing.html',locals())

def listing(request):
    user_id = request.session.get('user_id')
    user = UserProfile.objects.get_or_none(user_reference_id = user_id)
    project = Project.objects.get_or_none(slug =request.GET.get('slug'))
    project_user_relation = ProjectUserRoleRelationship.objects.get_or_none(id=user.id)
    activity_list = Activity.objects.filter(project = project).order_by('-id')
    
    task_list = Task.objects.filter(activity__project=project).order_by('-id')
#        task_list = get_tasks_list(activity_list)
    print activity_list,task_list
    milestone = Milestone.objects.filter(project=project).order_by('-id')
    project_funders = ProjectFunderRelation.objects.get_or_none(project = project)
    return render(request,'taskmanagement/atm-listing.html',locals())

def add_taskmanagement(request,model_name,m_form):
    try:
        project = Project.objects.get(slug = request.GET.get('slug'))
    except:
        project = Project.objects.get(slug= request.POST.get('slug_project'))
    user_id = request.session.get('user_id')
    user = UserProfile.objects.get(user_reference_id = user_id)
    form=eval(m_form)
    if request.method=='POST':
        form=form(user_id,project.id,request.POST,request.FILES)
        if form.is_valid():
            f=form.save()
            f.slug = f.name.replace(' ','-')
            f.save()
            if model_name == 'Activity' or model_name == 'Task':
                f.created_by = user
                f.save()
                return HttpResponseRedirect('/managing/listing/?slug='+project.slug)
            else :
                return HttpResponseRedirect('/managing/listing/?slug='+project.slug)
    else:
        form=form(user_id,project.id)
    return render(request,'taskmanagement/base_forms.html',locals())

def edit_taskmanagement(request,model_name,m_form,slug):
    user_id = request.session.get('user_id')
    user = UserProfile.objects.get(user_reference_id = user_id)
    form=eval(m_form)
    m=eval(model_name).objects.get(slug = slug)
    try:
        project = Project.objects.get(slug =request.GET.get('key') )
    except:
        project = Project.objects.get(slug = request.POST.get('slug_project'))
    if request.method == 'POST':
        form=form(user_id,project.id,request.POST,request.FILES,instance=m)
        if form.is_valid():
            f=form.save()
            f.slug = f.name.replace(' ','-')
            f.save()
            if model_name == 'Activity' or model_name == 'Task':
                f.created_by = user
                f.save()
                return HttpResponseRedirect('/managing/listing/?slug='+project.slug)
            else:
                return HttpResponseRedirect('/managing/listing/?slug='+project.slug)
    else:
         form=form(user_id,project.id,instance=m)
    return render(request,'taskmanagement/base_forms.html',locals())

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
    ids = request.GET.get('id[]')
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
    milestones= Milestone.objects.filter(project = project)
    for act in activity:
        tasks = Task.objects.filter(activity = act)
        total_tasks = len(tasks) + total_tasks
        for t in tasks:
            if t.end_date.strftime('%Y-%m-%d') <= datetime.now().strftime('%Y-%m-%d'):
                completed_tasks = completed_tasks + 1
    if completed_tasks != 0:
        percent =int((float(completed_tasks) / float(total_tasks))*100)
    else:
        percent = 0
    if milestones:
        total_milestones = len(milestones)
    data={'total_tasks':total_tasks,'completed_tasks':completed_tasks,'total_milestones':total_milestones,'percent':percent}
    return data


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
   
def my_tasks_listing(project):
    task_lists=[]
    activities = Activity.objects.filter(project = project)
    for i in activities:
        tasks = Task.objects.filter(active=2,activity=i).order_by('-created')
        for t in tasks:
            if t not in task_lists:
                task_lists.append(t)
    return task_lists
    
def updates(obj_list):
# to get the recent updates of the projects 
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
                if project.history.latest():
                    attach_lists = Attachment.objects.filter(active=2,content_type = ContentType.objects.get_for_model(project),object_id = project.id).order_by('created')
                    for a in attach_lists:
                        task_uploads={'project_name':project.name,'task_name':task.name,'attach':a.description,
                        'user_name':a.created_by.email if a.created_by else '','time':a.created.time(),'date':a.created.date(),'task_status':''}
                    uploads.append(task_uploads)
    try:
        if uploads:
            uploads = sorted(uploads, key=lambda key: key['date'],reverse=True)
        else:
            uploads = []
    except:
        uploads = uploads
    return uploads
        
def corp_task_completion_chart(obj_list):
# to get the task  and completion progress bar in the corporate dashboard
    data={}
    task_completion={}
    complete_status = []
    task_progress =[] 
    total_percent=[] 
    remaining =[] 
    if obj_list:
        for project in obj_list:
            total_tasks = project.total_tasks()
            tasks_completed_count = project.tasks_completed()
            try:
                percentage = int((float(tasks_completed_count) / float(total_tasks))*100)
            except:
                percentage = 0
            remaining_percent = 100 - percentage if percentage !=0 else 0
            total_percent.append(str(percentage))
            progress = str(project.name)+ ' ' + str(percentage)+'%'
            task_progress.append(str(progress))
            remaining.append(int(remaining_percent))
            data = int(percentage)
            complete_status.append(data)
        task_completion = {'x_axis': task_progress,'remaining':remaining,'data':complete_status}
    return task_completion
 
def task_offset_date(task):
    task = Task.objects.get(id = int(task))
    start_date = task.start_date.strftime('%y-%m-%d')
    end_date = task.end_date.strftime('%y-%m-%d')
    offset = end_date - start_date
    

def corp_total_budget(obj_list):
# bar chart for the total budget in corporate dashboard
    total_budget=[]
    utilized_budget=[]
    project_list=[]
    corp_budget={}
    disbursed=[]
    planned_cost = utilized_cost =disbursed_amount= 0
    if obj_list:
        for project in obj_list:
            budget_details = project.project_budget_details()
            planned_cost = float(budget_details.get('planned_cost') or 0)/10000000
            utilized_cost = float(budget_details.get('utilized_cost') or 0)/10000000
            disbursed_budget = float(budget_details.get('disbursed_cost') or 0)/10000000
            total_budget.append(planned_cost)
            utilized_budget.append(utilized_cost)
            disbursed.append(disbursed_budget)
            project_list.append(str(project.name))
        corp_budget = {'projects':project_list,'total_budget':total_budget,'utilized':utilized_budget,'disbursed':disbursed}
    return corp_budget

def corp_total_budget_disbursed(obj_list):
    total_budget=[]
    utilized_budget=[]
    total_disbursed={}
    disbursed_amount=[]
    total =disbursed=0
    if obj_list:
        for project in obj_list:
            try:
                budget = project.project_budget_details()
                planned_cost = float(budget.get('planned_cost') or 0)/10000000
                utilized_cost = float(budget.get('utilized_cost') or 0)/10000000
                disbursed_budget = float(budget.get('disbursed_cost') or 0)/10000000
                total_budget.append(planned_cost)
                utilized_budget.append(utilized_cost)
                disbursed_amount.append(disbursed_budget)
            except:
                total = 0
                disbursed=0
        total = sum(total_budget)
        total_percentage = 100
        disbursed = sum(disbursed_amount)
        try:
            disbursed_percent =int((disbursed/total)*100) if int(disbursed) > 0 else 0
        except:
            disbursed_percent = 0
        total_disbursed = {'total':total,'disbursed':disbursed,'total_percent':total_percentage,'disbursed_percent':disbursed_percent}
    return total_disbursed 


def get_tasks_list(activity_list):
    task_list=[]
    for i in activity_list:
        task = Task.objects.filter(activity = i).order_by('-id')
        for i in task:
            if i not in task_list:
                task_list.append(i)
    return task_list


def my_tasks_details(request):
    user_id = request.session.get('user_id')
    user = UserProfile.objects.get(user_reference_id = user_id)
    project = Project.objects.get(slug =request.GET.get('slug'))
    project_user_relation = ProjectUserRoleRelationship.objects.get(id=user.id)
    project_funders = ProjectFunderRelation.objects.get_or_none(project = project)
    tasks_list = my_tasks_listing(project)
    return render(request,'taskmanagement/my-task.html',locals())
