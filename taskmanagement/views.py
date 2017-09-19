import requests,ast
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
from projectmanagement.models import (Project,UserProfile,
    ProjectFunderRelation)
from media.models import Attachment
from budgetmanagement.models import *
from userprofile.models import ProjectUserRoleRelationship
from dateutil import parser
from datetime import timedelta
from itertools import chain
from rest_framework.views import APIView
from rest_framework.response import Response as RestResponse
from serializers import *
from rest_framework.response import Response
from pmu.settings import PMU_URL

# Create your views here.

def listing(request):
    user_id = request.session.get('user_id')
    user = UserProfile.objects.get_or_none(user_reference_id = user_id)
    project = Project.objects.get_or_none(slug =request.GET.get('slug'))
    project_user_relation = ProjectUserRoleRelationship.objects.get_or_none(id=user.id)
    activity_list = Activity.objects.filter(project = project).order_by('-id')
    
    task_list = Task.objects.filter(activity__project=project).order_by('-id')
    milestone = Milestone.objects.filter(project=project).order_by('-id')
    project_funders = ProjectFunderRelation.objects.get_or_none(project = project)
    import json
    data = {'project_id':int(project.id)}
    rdd = requests.get(PMU_URL +'/managing/gantt-chart-data/', data=data)
    taskdict = ast.literal_eval(json.dumps(rdd.content))
    return render(request,'taskmanagement/atm-listing.html',locals())

def add_taskmanagement(request,model_name,m_form):
    key=''
    try:
        project = Project.objects.get(slug = request.GET.get('slug'))
    except:
        project = Project.objects.get(slug= request.POST.get('slug_project'))
    user_id = request.session.get('user_id')
    user = UserProfile.objects.get_or_none(user_reference_id = user_id)
    budget = Budget.objects.get_or_none(project = project,active=2)
    form=eval(m_form)
    if budget:
        if request.method=='POST':
            form=form(user_id,project.id,request.POST,request.FILES)
            if form.is_valid():
                f=form.save()
                from projectmanagement.common_method import unique_slug_generator
                f.slug = unique_slug_generator(f,key)
                f.save()
                if model_name == 'Activity' or model_name == 'Task':
                    f.created_by = user
                    f.save()
                    return HttpResponseRedirect('/managing/listing/?slug='+project.slug)
                else :
                    return HttpResponseRedirect('/managing/listing/?slug='+project.slug)
        else:
            form=form(user_id,project.id)
    else:
        message = "Budget is not added"
    return render(request,'taskmanagement/base_forms.html',locals())

def edit_taskmanagement(request,model_name,m_form,slug):
    key=''
    user_id = request.session.get('user_id')
    user = UserProfile.objects.get_or_none(user_reference_id = user_id)
    form=eval(m_form)
    m=eval(model_name).objects.get_or_none(slug = slug)
    try:
        project = Project.objects.get(slug =request.GET.get('key') )
    except:
        project = Project.objects.get(slug = request.POST.get('slug_project'))
    if request.method == 'POST':
        form=form(user_id,project.id,request.POST,request.FILES,instance=m)
        if form.is_valid():
            f=form.save()
            from common_method import unique_slug_generator
            f.slug = unique_slug_generator(f,key)
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
    obj = model.model_class().objects.get_or_none(id=int(ids))
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
#to get the startdate as project start date on selecting the activity and list the tasks based on activities
    start_date = ''
    tasks = []
    ids = request.GET.get('id')
    url=request.META.get('HTTP_REFERER')
    obj = None
    try:
        
        obj = Activity.objects.get_or_none(active=2,id= int(ids))
        project = Project.objects.get_or_none(id = obj.project.id)
        tasks = Task.objects.filter(active=2,activity__project=project)
        start_date = project.start_date.strftime('%Y-%m-%d')
        
    except:
        obj = None
    if obj.activity_type == 2 :
        tasks = []
    else:
        tasks = [{'id':i.id,'name':i.name} for i in tasks]
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
# to get the overdue of the milestone i.e getting the max end date of the tasks tagged to the milestone
    task_ids = request.GET.get('id')
    url=request.META.get('HTTP_REFERER')
    tasks_obj = Task.objects.filter(id__in = eval(task_ids)).values_list('end_date',flat = True)
    try:
        milestone_overdue = max(tasks_obj).strftime('%Y-%m-%d')
    except:
        milestone_overdue = tasks_obj[0]
    return JsonResponse({"milestone_overdue_date":milestone_overdue})

from datetime import datetime
#slug = Project slug and this is to display in project summary dashboard
def total_tasks_completed(slug):
    total_tasks = completed_tasks=total_milestones = 0
    milestones = []
    project = Project.objects.get_or_none(slug = slug)
    activity = Activity.objects.filter(project=project)
    milestones= Milestone.objects.filter(project = project)
    tasks = Task.objects.filter(activity__project = project)
    total_tasks = tasks.count()
    for t in tasks:
        if t.status == 2:
            completed_tasks = completed_tasks + 1
    if completed_tasks != 0:
        percent =int((float(completed_tasks) / total_tasks)*100)
    else:
        percent = 0
    if milestones:
        total_milestones = milestones.count()
    data={'total_tasks':total_tasks,'completed_tasks':completed_tasks,'total_milestones':total_milestones,'percent':percent}
    return data


def my_tasks_listing(project):
# to get the tasks which is overdue to today 
    today = datetime.today().date()
    task_lists=[]
    activities = Activity.objects.filter(project = project)
    tasks_list = Task.objects.filter(activity__project = project,start_date__lt = today).order_by('-start_date')
    return tasks_list
    
def get_project_updates(project,uploads):
    #get project updates 
    if project.history.latest():
        attach_lists = Attachment.objects.filter(active=2,content_type = ContentType.objects.get_for_model(project),object_id = project.id).order_by('created')
        for a in attach_lists:
            uploads.append({'project_name':project.name,'task_name':'','attach':a.description,
            'user_name':a.created_by.email if a.created_by else '','time':a.created,'date':a.created.date(),'task_status':''})
    return uploads
    
def get_tasks_status(project,task,uploads):
    #to get the task status updates 
    if task.status == 2 and task.history.latest():
        uploads.append({'project_name':project.name,'task_name':task.name,'attach':'',
            'user_name':task.created_by.email if task.created_by else '','time':task.modified,'date':task.modified.date(),'task_status':task.history.latest()})
    return uploads
 
def updates(obj_list):
# to get the recent updates of the projects 
    formats = '%H:%M %p'
    uploads = []
    task_completed = {}
    completed_tasks = []
    task_uploads = {}
    for project in obj_list:
        project = Project.objects.get_or_none(id = int(project.id))
        uploads = get_project_updates(project,uploads)
        activity = Activity.objects.filter(project=project)
        task_list = Task.objects.filter(activity__project = project)
        for task in task_list:
            attach_list = Attachment.objects.filter(active=2,content_type = ContentType.objects.get_for_model(task),object_id = task.id).order_by('created')
            for attach in attach_list:
                uploads.append({'project_name':project.name,'task_name':task.name,'attach':attach.description,
                'user_name':attach.created_by.email if attach.created_by else '','time':attach.created,'date':attach.created.date(),'task_status':task.history.latest()})
            uploads = get_tasks_status(project,task,uploads)
    try:
        uploads = sorted(uploads, key=lambda key: key['date'],reverse=True)
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
                planned_cost = budget.get('planned_cost') or 0 
                utilized_cost = budget.get('utilized_cost') or 0
                disbursed_budget = budget.get('disbursed_cost') or 0
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
            disbursed_percent = (float(disbursed)/total)*100 if int(disbursed) > 0 else 0
        except:
            disbursed_percent = 0
        total_disbursed = {'total':convert_budget(total),'disbursed':convert_budget(disbursed) if disbursed else 0,'total_percent':total_percentage,'disbursed_percent':int(disbursed_percent)}
    return total_disbursed 


def my_tasks_details(request):
    image_url = PMU_URL
    today = datetime.today().date()
    tomorrow = today + timedelta(days=1)
    remain_days = today + timedelta(days=2)
    user_id = request.session.get('user_id')
    user = UserProfile.objects.get_or_none(user_reference_id = user_id)
    project = Project.objects.get_or_none(slug =request.GET.get('slug'))
    project_user_relation = ProjectUserRoleRelationship.objects.get_or_none(id=user.id)
    over_due = my_tasks_listing(project)
    tasks_today = project.get_todays_tasks(today)
    tasks_tomorrow = project.get_todays_tasks(tomorrow)
    remain_tasks = project.get_remaining_tasks(remain_days)
    task_listing = list(chain(over_due ,tasks_today ,tasks_tomorrow,remain_tasks))
    
    return render(request,'taskmanagement/my-task.html',locals())
    
    
def task_comments(request):
    msg =""
    application_type = {'application':2,'pdf':2,'vnd.ms-excel':2,'msword':2,'image':1}
    doc_type = {'application':3,'pdf':2,'vnd.ms-excel':1,'msword':4,'image':None}
    url=request.META.get('HTTP_REFERER')
    MAX_UPLOAD_SIZE = "5242880"
#   "2621440" 
    user_id = request.session.get('user_id')
    user = UserProfile.objects.get_or_none(user_reference_id = user_id)
    from media.models import Comment
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        task = Task.objects.get_or_none(id=task_id)
        try:
            task.task_progress = request.POST.get('child2')
            task.status = 2 if request.POST.get('child2') == 100 else 3 
            task.save()
            task.actual_end_date = task.modified.date() if task.task_progress == 100 else task.actual_end_date
            task.save()
            task.actual_start_date = task.modified.date() if not task.actual_start_date else task.actual_start_date 
            task.save()
        except:
            pass
        if request.FILES:
            upload_file = request.FILES.get('upload_attach')
            file_type = upload_file.content_type.split('/')[0]
            if upload_file.size <= MAX_UPLOAD_SIZE:
                attach = Attachment.objects.create(description = request.POST.get('comment'),
                    attachment_type = application_type.get(file_type),
                    document_type = doc_type.get(file_type),
                    attachment_file = request.FILES.get('upload_attach'),
                    created_by= user,content_type = ContentType.objects.get(model=('task')),
                    object_id = request.POST.get('task_id'))
                attach.save()
            else:
                msg = "yess"
        elif request.POST.get('comment')!= '':
            comment = Comment.objects.create(text = request.POST.get('comment'),
                created_by = user,content_type = ContentType.objects.get(model=('task')),
                object_id = request.POST.get('task_id'))
            comment.save()
        return HttpResponseRedirect(url+'&key='+task.slug+'&msg='+msg)
    return HttpResponseRedirect(url)

''' Jagpreet Added Code below for Tasks' Expected Start Date and Expected End Date''
from dateutil import parser
'''
from datetime import timedelta, time

def get_tasks_objects(request):
    ids = request.GET.get('id')
    url=request.META.get('HTTP_REFERER')
    obj = None
    start_dates=[]
    task_list = Task.objects.filter(active=2,id__in = eval(ids))
    populated_dates = ExpectedDatesCalculator(**{'task_list':task_list})
    expected_dates = populated_dates.data
    for key,value in expected_dates.items():
        start_dates.append(value.get('expected_end_date'))
    expected_end_date = max(start_dates).strftime('%Y-%m-%d')
    return JsonResponse({"calculation":expected_end_date})

class ExpectedDatesCalculator():

    """ This class takes a task  or a list of tasks ActiveQuery Objects and
    populates it with expected start date and expected end date.
    ***** USAGE *****
    > task1=Task.objects.get(pk=1)
    > ExpectedDatesCalculator(task=task1)
    > task1.expected_end_date
      <Prints datetime object>
    > task1.expected_start_date
      <prints datetime object>
    """
    
    def __init__(self, task=None, task_list=None):
        ''' Initialize the class
            task_id - optional the task whose dates are to be calculated
            task_list - optional tasks whose dates are to be populated
        '''
        if(task is not None):
            self.task = task
            self.data = {}
            self.populate_expected_start_end_date()

        elif (task_list is not None):
            self.task_list = task_list
            self.data = {}
            for task in self.task_list:
                self.populate_expected_start_end_date(task)

        else:
            self.task_list = []
            self.data = {}

    # Helper function gets next weekday if next day is weekend
    @staticmethod
    def next_weekday(somedate):
        ret = somedate + timedelta(days=1)
        day = somedate.strftime('%a')
        if day == 'Fri':
            ret = somedate + timedelta(days=3)
        elif day == 'Sat':
            ret = somedate + timedelta(days=2)
        return ret

    def populate_expected_start_end_date(self, itask=None):
        # Get expected start_date of dependent tasks
        # returns the same task with expected dates populated
        if(itask is None):
            taskid = self.task.id
            itask = self.task
        else:
            taskid = itask.id

        # if expected dates are already calculated
        if (taskid in self.data.keys()):

            expected = self.data[taskid]
            itask.expected_start_date = expected['expected_start_date']
            itask.expected_end_date = expected['expected_end_date']
            return itask


        main_task = itask

        # If actual dates are populated, return those
        if (main_task.actual_end_date):
            main_task.expected_start_date = main_task.actual_start_date
            main_task.expected_end_date = main_task.actual_end_date

            ret = {'expected_start_date': main_task.actual_start_date,
                   'expected_end_date': main_task.actual_end_date}

            self.data[taskid] = ret
            return main_task

        else:
            # Otherwise recursively get expected start date of all ancestors
            dependencies = Task.objects.filter(
                task_dependency=taskid)  # .filter(status=2)
            dep_dates = []
            for dependency in dependencies:
                print("Task ID:", main_task.id, " Dependency:", dependency.id)
                dep_dates.append(self.populate_expected_start_end_date(
                    dependency))

            # Put expectedstart date as next weekday end date of latest dependent task
            # unless expected start/end date is less than the planned one
            expected_start_date = main_task.start_date
            expected_end_date = main_task.end_date
            if(len(dep_dates) > 0):
                for dep in dep_dates:
                    expected_start_date = self.next_weekday(dep.expected_end_date) if (self.next_weekday(
                        dep.expected_end_date) > expected_start_date) else expected_start_date
                expected_end_date = expected_start_date + \
                    (main_task.end_date - main_task.start_date)
                expected_end_date = self.next_weekday(
                    expected_end_date - timedelta(days=1))

            ret = {'expected_start_date': expected_start_date,
                   'expected_end_date': expected_end_date}
            self.data[taskid] = ret
            main_task.expected_start_date = ret['expected_start_date']
            main_task.expected_end_date = ret['expected_end_date']
            return main_task


def get_descendants(task):
    descendants = Task.objects.filter(task_dependency=task.id)
    ret_descendants = Task.objects.filter(
        task_dependency=task.id)
    for descendant in descendants.all():
        ret_descendants = (
            ret_descendants | get_descendants(descendant))
    return ret_descendants


def get_ancestors(task):
    ancestors = task.task_dependency
    ret_ancestors = task.task_dependency
    for ancestor in ancestors.all():
        ret_ancestors = (ret_ancestors | get_ancestors(ancestor))
    return ret_ancestors


def related_tasks(project_id, i_task=None, activity=None, milestone=None):
    tasks = Task.objects.filter(activity__project=project_id)
    task = Task.objects.get(pk=i_task)
    if (task is None):
        return tasks
    if (task is not None):
        # traverse up
        # traverse down
        descendants = get_descendants(task)
        ancestors = get_ancestors(task)
        return (descendants | ancestors).distinct()


class GanttChartData(APIView):

    def get(self, request, format=None):
        '''
         Get Main Task ( if any)
         Get Related Tasks
         Get Milestones
         Get Activity and Super Category
         Serialize data
         Send back json response
        '''
        tasks = None
        i_project_id = request.data.get('project_id')
        tasks = Task.objects.filter(activity__project=i_project_id)
        activities = Activity.objects.filter(project=i_project_id)
        milestones = Milestone.objects.filter(project=i_project_id)
        supercategories = SuperCategory.objects.filter(project=i_project_id)
        ExpectedDatesCalculator(task_list=tasks)
        taskdict = {}
        taskdict['tasks'] = TaskSerializer(tasks, many=True).data
        taskdict['activities'] = ActivitySerializer(activities, many=True).data
        taskdict['milestones'] = MilestoneSerializer(
            milestones, many=True).data
        taskdict['supercategories'] = SuperCategorySerializer(
            supercategories, many=True).data
        return Response(taskdict)
        
        
def convert_budget(val):
    """Convert the Values to Rs,Lakhs,Crores."""
    import locale
    import re
    loc = locale.setlocale(locale.LC_MONETARY, 'en_IN')
    val = float('{:.2f}'.format(float(val)))
    if val <= 99999.99:
        val = re.sub(u'\u20b9', ' ', locale.currency(val, grouping=True).decode('utf-8')).strip()
        return re.sub(r'\.00', '', val)
    elif val >= 100000.99 and val <= 9999999.99:
        val = re.sub(u'\u20b9', ' ', locale.currency(val / 100000, grouping=True).decode('utf-8')).strip()
        return str(float(val)) + ' ' + 'Lac'
    else:
        h = locale.format("%d", val)
        val = float(h) * (0.0001 / 1000)
        val = '{:.2f}'.format(val)
        return str(float(val)) + ' ' + 'Cr'

from django.http import JsonResponse        
def get_activites_list(request):
    ids = request.GET.get('id')
    url=request.META.get('HTTP_REFERER')
    obj = None
    activity=[]
    obj_list = Activity.objects.filter(active=2,super_category__in = eval(ids))
    activity.append({'id':'undefined','name':'-----'})
    activity = [{'id':i.id,'name':i.name} for i in obj_list]
    return JsonResponse({"activity":activity})
