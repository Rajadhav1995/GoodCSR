from django import template
register = template.Library()
from datetime import datetime
from media.models import Comment,Attachment
from django.contrib.contenttypes.models import ContentType
import pytz
import requests,ast
from taskmanagement.models import Task
from budgetmanagement.models import *
from projectmanagement.models import Project,UserProfile,ProjectFunderRelation,ProjectParameter
from pmu.settings import PMU_URL,SAMITHA_URL
from ast import literal_eval
from itertools import chain
from operator import is_not
from functools import partial
# from dashboard.project_wall import string_trim


#According to Wikipedia the exact definition of a goal is:
# A desired result a person or a system envisions, plans and commits to achieve a personal or organizational desired end-point in some sort of assumed development. Many people endeavor to reach goals within a finite time by setting deadlines. 
#In other words, any planning you do for the future regardless of what it is, is a goal. 
#So the next time you are planning on doing the weekly chores or decide on watching that really cool action movie after work, always keep in mind that these small tasks account as goals and while seemingly insignificant you are goal setting.
# Just like how sunlight can't burn through anything without a magnifying glass focusing it, 
#you can't achieve anything unless a goal is focusing your effort. 
#Because at the end of the day goals are what give you direction in life. 
#By setting goals for yourself you give yourself a target to shoot for. 
#This sense of direction is what allows your mind to focus on a target and rather than waste energy shooting aimlessly,
# allows you to hit your target and reach your goal. 
#By setting goals for yourself you are able to measure your progress because you always have a fixed endpoint or benchmark to compare with. Take this scenario for example: David makes a goal to write a book with a minimum of 300 pages. He starts writing every day and works really hard but along the way, he loses track of how many more pages he has written and how much more he needs to write. 
#So rather than panicking David simply counts the number of pages he has already written and he instantly determines his progress and knows how much further he needs to go.

@register.assignment_tag
def get_details(obj):
    closed_tasks = update = ''
    formats = '%I:%M %p'
    user = obj.get('user_name') or ''
    task_name = obj.get('task_name') or ''
    project = obj.get('project_name') or ''
    time_zone= obj.get('time').replace(tzinfo = pytz.utc) if obj.get('time') else ''
    convert_time = time_zone.astimezone(pytz.timezone('Asia/Kolkata'))
    time = convert_time.strftime(formats)
    date = obj.get('date').strftime('%d %B %Y') if obj.get('date') else ''
    description = obj.get('attach') or ''
    task_status = obj.get('task_status') or ''
    file_type = obj.get('file_type') or ''
    if task_status and task_status.status == 2:
        closed_tasks = '''<li><canvas class="user-icon" data-name=" '''+ user +'''" width="30" height="30" style="border-radius:40px; float:left;" ></canvas> <div class="update-pad">'''+user + ''' completed <u>'''+ task_name + ' - ' + project + '''</u> <span>'''+ str(date)+' '+ str(time) + '''</span></div></li>'''
    update = '''<li><canvas class="user-icon" data-name=" '''+ user +'''" width="30" height="30" style="border-radius:40px; float:left;" ></canvas> <div class="update-pad">'''+user + ''' uploaded <u>'''+ file_type +'''</u> in <u> '''+ project + '''</u> <span>'''+ str(date)+' '+str(time) + '''</span></div></li>'''

    return update,closed_tasks 
    
@register.assignment_tag   
def task_comments(date,task_id):
    attach={}
    task_comment=[]
    
    comment_list = Comment.objects.filter(active=2,content_type=ContentType.objects.get(model=('task')),object_id=task_id).order_by('-id')
    for i in comment_list.filter(created__range = (datetime.combine(date, datetime.min.time()),datetime.combine(date, datetime.max.time()))):
        task_comment.append(i)
    return task_comment

def task_progress_history_details(task_data,attach_obj,i,comment_obj):
    utc=pytz.UTC
    if not attach_obj:
        if comment_obj and (i.get_previous_by_created().task_progress != i.task_progress):
        # if i.get_previous_by_created().task_progress != i.task_progress:
            cell_one = {'name':comment_obj.created_by.attrs,'comment_text':comment_obj.text,'date':i.modified,
                'task_progress':i.task_progress,'attachment':0,
                'previous_task_progress':i.get_previous_by_created().task_progress,}
            task_data.append(cell_one)
        elif (i.get_previous_by_created().task_progress != i.task_progress):
            
            cell_one = {'name':'','comment_text':'','date':i.modified,
                'task_progress':i.task_progress,'attachment':0,
                'previous_task_progress':i.get_previous_by_created().task_progress,}
            task_data.append(cell_one)
        elif comment_obj and (i.get_previous_by_created().task_progress == i.task_progress):
            cell_one = {'name':comment_obj.created_by.attrs,'comment_text':comment_obj.text,'date':i.modified,
                'task_progress':i.task_progress,'attachment':0,
                'previous_task_progress':i.get_previous_by_created().task_progress}
            task_data.append(cell_one)
        
    elif attach_obj:
        attachment_data = {'name':attach_obj.created_by.attrs,
            'description':attach_obj.description,
            'date':attach_obj.created,'attachment':1,
            'attachment_type':attach_obj.attachment_type,
            'document_type':attach_obj.document_type,
            'image_url':PMU_URL + attach_obj.attachment_file.url,
            'task_progress':i.task_progress,
            'previous_task_progress':i.get_previous_by_created().task_progress,
            'file_name':attach_obj.name}
        task_data.append(attachment_data)
    return task_data

def get_modified_by_user(user_id):
    if user_id:
        user_object = UserProfile.objects.get_or_none(user_reference_id=int(user_id))
    else:
        user_object = ''
    if user_object:
        return user_object.attrs

def task_updates_list(key,task_progress,start_date,end_date):
# this is to get the task updates 
# where the combination of updates would be filtered and displayed
    task_data = []
    utc=pytz.UTC
    slug = task_progress.activity.project.slug
    if key == 'project_tasks':
        task_progress_history = task_progress.history.filter(task_progress__isnull=False,modified__range = [start_date,end_date]).order_by('-id')
    else:
        task_progress_history = task_progress.history.filter(created__range=[start_date,end_date]).order_by('-id')
    temp_var = 0
    for i in task_progress_history:
        new_var = int(i.modified.strftime("%Y%m%d%H%M%S"))
        
        if (int(new_var)-int(temp_var)) > 10 and i.task_progress:
            
            previous_task_progress = i.get_previous_by_created().task_progress
            task_time = i.modified
            next_tick = task_time.second +1
            
            task_prev_tick = task_time.second -1

            try:
                start_time = task_time.replace(microsecond=499999,second=task_prev_tick)
            except:
                start_time = task_time.replace(microsecond=499999,second=59)
            end_time = task_time.replace(microsecond=999999)
            
            attach_obj = Attachment.objects.get_or_none(created__range=(start_time,end_time),content_type=ContentType.objects.get(model=('task')),object_id=task_progress.id)
            comment_obj = Comment.objects.get_or_none(active=2,content_type=ContentType.objects.get(model=('task')),object_id=task_progress.id,\
                        created__range=(start_time,end_time))     
            if key == 'project_tasks': 
                # this for project tasks updates section 
                task_data = task_progress_history_details(task_data,attach_obj,i,comment_obj)
                
            else:
                # this is for updates wall
#                if previous_task_progress != i.task_progress:
                history_data = get_task_attachment(i,attach_obj,previous_task_progress,slug,comment_obj)
                task_data.append(history_data)
        temp_var = new_var
    return task_data

def get_task_attachment(obj,attach_obj,previous_task_progress,slug,comment_obj):
    history_data = {'task_name':obj.name,'activity_name':obj.activity.name,
                'supercategory':obj.activity.super_category,'date':obj.modified,
                'task_progress':obj.task_progress,'previous_task_progress':previous_task_progress,
                'update_type':'tasks_history','created_by':obj.created_by,'modified_by':get_modified_by_user(obj.modified_by),
                'task_link':PMU_URL+'/managing/my-tasks/details/?slug='+slug+'&key=projecttasks&status=1'}
    if attach_obj:
        attachment_file_type = get_attachment_type(attach_obj.attachment_file.url.split('/')[-1])
        history_data.update({'file_name':string_trim(attach_obj.attachment_file.url.split('/')[-1]) if attach_obj.attachment_file else '','file_description':attach_obj.description,'file_url':PMU_URL + '/' +str(attach_obj.attachment_file),'attachment_file_type':attachment_file_type})
    if comment_obj:
        history_data.update({'comment_text':comment_obj.text})
    return history_data

@register.assignment_tag
def task_comments_progress(date,task_id, attach):
    task_data = []
    key = 'project_tasks'
    start_date = datetime.combine(date, datetime.min.time())
    end_date = datetime.combine(date, datetime.max.time())
    task_progress = Task.objects.get(id=task_id)
    # to make common function for project tasks updates and updates wall (tasks history objects)
    # based on the key ,task , start date and end date we are getting the details ,
    # particular task
    task_data = task_updates_list(key,task_progress,start_date,end_date)
    # task_data.append(attachment_json_for_comments(task_id,attach))
    task_data = filter(partial(is_not, None), task_data)
    task_data.sort(key=lambda item:item['date'], reverse=True)
    return task_data

def attachment_json_for_comments(task_id,attach):
    attachment_data = []
    for i in attach:
        time = i.created
        
        next_tick = time.second +1
        prev_tick = time.second -1
        try:
            start_time = time.replace(microsecond=499999,second=prev_tick)
        except:
            start_time = time.replace(microsecond=499999,second=59)

        end_time = time.replace(microsecond=999999)
        task_object = Task.objects.get(id=task_id)
        try:
            task_history = task_object.history.get(modified__range = (start_time,end_time))
        except:
            task_history = task_object.history.filter(modified__range = (start_time,end_time))
            if task_history:
                task_history = task_history[0]
        # import ipdb;ipdb.set_trace()
        if task_history:

            attachment_data = {'name':i.created_by.attrs,
            'description':i.description,
            'date':i.created,'attachment':1,
            'attachment_type':int(i.attachment_type),
            'document_type':i.document_type,
            'image_url':PMU_URL + i.attachment_file.url,
            'task_progress':task_history.task_progress,
            'previous_task_progress':task_history.get_previous_by_created().task_progress,
            'file_name':i.attachment_file.name.split('/')[-1]}
    return attachment_data

@register.assignment_tag
def get_task_status(task_id):
    task_progress = Task.objects.get(id=task_id)
    task_progress_history = task_progress.history.filter(task_progress__isnull=False)
    if task_progress_history:
        status = 1
    else:
        status = 0
    return status

from datetime import date
@register.assignment_tag
def get_task_comments(comment_date,task_id):
    comment_data = {}
    try:
        prev_tick = comment_date.second -1
    except:
        pass
    try:
        start_time = comment_date.replace(microsecond=499999,second=prev_tick)
    except:
        start_time = comment_date.replace(microsecond=499999,second=59)

    end_time = comment_date.replace(microsecond=999999)
    comment_list = Comment.objects.latest_one(active=2,content_type=ContentType.objects.get(model=('task')),object_id=task_id,\
                        created__range=(start_time,end_time))
    if comment_list:
        comment_data = {'name':comment_list.created_by.attrs,'comment_text':comment_list.text,'time':comment_list.created}
    return comment_data

def get_removed_questions(questions,block,project_report,block_type,quest_removed):
    # to get the removed questions list for that particular block 
    removed_ques=[]
    parent_ques=[]
    final_questions=[]
    remove_id=''
    quest_list = RemoveQuestion.objects.get_or_none(quarter_report=project_report,block_type=block_type)
    if quest_list and quest_list.text != None:
        remove_id = quest_list.id
        for i in eval(quest_list.text):
            ques = Question.objects.get_or_none(id=int(i))
            if ques.parent == None:
                parent_ques.append(ques)
#                added by meghana
                removed_ques.append(ques)
#                ends
            else:
                removed_ques.append(ques)
        if quest_removed == 'false':
            final_questions = questions.exclude(id__in =[rmv.id for rmv in removed_ques ]).order_by('id')
            fianl_questions = list(chain(final_questions)).extend(list(chain(questions.filter(id__in = [pt.id for pt in parent_ques]).order_by('id'))))
            
        else:
            final_quest = questions.filter(id__in = [rmv.id for rmv in removed_ques]).values_list('id',flat=True)
            main_quest = Question.objects.filter(block=block).exclude(parent=None)[0]
            final_quest=map(int,final_quest)
            final_quest.append(int(main_quest.parent.id))
            final_questions = Question.objects.filter(id__in = final_quest).order_by('id') 
    elif not quest_list and quest_removed == 'true':
        remove_id = ''
        final_questions =[]
    else:
        remove_id =''
        final_questions = questions
    return final_questions,remove_id
    
def get_removed_populate_questions(questions,project_report,block_type,quest_removed):
    # to get the removed questions list which are auto populated questions for that particular block
    removed_ques=[]
    remove_id=''
    quest_list = RemoveQuestion.objects.get_or_none(quarter_report=project_report,block_type=block_type)
    if quest_list and quest_list.text != None :
        remove_id = quest_list.id
        for i in eval(quest_list.text):
            ques = Question.objects.get_or_none(id=int(i))
            if ques.parent != None:
                removed_ques.append(ques)
        if quest_removed == 'false':
            final_questions = questions.exclude(id__in = eval(quest_list.text)).order_by('id')
        else:
            final_questions = questions.filter(id__in = [rmv.id for rmv in removed_ques]).order_by('id')
    elif not quest_list and quest_removed == 'true':
        remove_id = ''
        final_questions =[]
    else:
        remove_id =''
        final_questions = questions
    return final_questions,remove_id
    
@register.assignment_tag 
def get_questions(block,project_report,block_type,quest_removed):
    # to get the questions that are tagged in that particular section
    question_list = []
    question_dict={} 
    report_obj=ProjectReport.objects.get_or_none(id=project_report.id)
    questions = Question.objects.filter(block=block,parent=None,block__block_type=0)
    final_questions,removed_id = get_removed_questions(questions,block,project_report,block_type,quest_removed)
    for i in final_questions:
        answer = Answer.objects.get_or_none(active=2,question = i,content_type=ContentType.objects.get_for_model(report_obj),object_id=report_obj.id)
        question_dict = {'q_id':i.id,'q_text':i.text,
            'q_type':i.qtype,'q_name':i.slug}
        if answer and (i.qtype == 'T' or i.qtype == 'ck'):
            question_dict['answer'] = answer.text 
        elif i.qtype == 'F':
            question_dict['answer'] = answer.attachment_file.url if answer and answer.attachment_file else ""
        question_list.append(question_dict)
    return question_list,removed_id

@register.assignment_tag 
def get_auto_populated_questions(ques_id,project,project_report,block_type,quest_removed):
    # to get the auto populated questions that are tagged to that particular section
    data = {}
    question = Question.objects.get_or_none(id=ques_id)
    sub_quest_list = []
    sub_questions = Question.objects.filter(parent = question,block__block_type=0)
    final_questions,remove_id = get_removed_populate_questions(sub_questions,project_report,block_type,quest_removed)
    mapping_view = ProjectFunderRelation.objects.get_or_none(project=project)
    cover_image = Attachment.objects.get_or_none(description__iexact = "cover image",attachment_type = 1,
            content_type = ContentType.objects.get_for_model(project_report),
            object_id = project_report.id)
    # details dict is to get the details of two sections on first click of generate report
    details = {'report_type':project_report.get_report_type_display(),
        'report_duration':project_report.start_date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d")+' TO '+project_report.end_date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d"),
        'prepared_by':project_report.created_by.attrs.get('first_name')+' '+project_report.created_by.attrs.get('last_name'),'client_name':mapping_view.funder.organization,
        'report_name': project_report.name if project_report.name else '',
        'cover_image': cover_image.attachment_file.url if cover_image else '',
        'project_title':project.name,'project_budget':project.total_budget,
        'donor':mapping_view.funder.organization,
        'program_description':project.summary if project.summary else '',
        'project_objective':project.program_aim if project.program_aim else '',
        'implement_ngo':mapping_view.implementation_partner.organization,
        'no_of_beneficiaries':project.no_of_beneficiaries,'project_duration':project.start_date.strftime('%Y-%m-%d')+' TO '+project.end_date.strftime('%Y-%m-%d'),
        'location':project.get_locations()}
    # to get the answers of auto populated questions 
    sub_quest_list = get_sub_answers(details,final_questions,project_report,project)
    return sub_quest_list,remove_id
    
@register.assignment_tag 
def get_milestones(quarter,report_obj,type_id):
# to get the milestones or activities that are save for particular quarters
    report_miles = []
    data = {}
    slug = {1:'milestone-section',2:'activity-section'}
    question = Question.objects.get_or_none(slug=slug.get(type_id))
    
    answer = Answer.objects.get_or_none(question=question,quarter = quarter,content_type=ContentType.objects.get_for_model(report_obj),object_id=report_obj.id)
    if answer:
        milestones = answer.inline_answer if answer else ''
        miles_list = ReportMilestoneActivity.objects.filter(id__in = eval(milestones))
        for i in miles_list:
            data = {'name':i.name,'description':i.description,'id':i.id}
            report_miles.append(data)
    return report_miles

@register.assignment_tag 
def get_mile_images(mile_id):
#to get the milestone and activity images 
    data = {}
    image_miles= []
    if mile_id:
        miles_obj =  ReportMilestoneActivity.objects.get_or_none(id=mile_id)
        image_miles= Attachment.objects.filter(content_type = ContentType.objects.get_for_model(miles_obj),object_id = miles_obj.id)
    return image_miles
    
def get_sub_answers(details,sub_questions,project_report,project):
# to get the answers of auto populated questions calculating based on whether there is answer object to that question 
    data = {}
    sub_quest_list = []
    keys = details.keys()
    for sub in sub_questions:
        data = {'q_id':sub.id,'q_text':sub.text,'q_type':sub.qtype,'q_name':sub.slug}
        answer_obj = Answer.objects.get_or_none(active=2,question=sub,content_type=ContentType.objects.get_for_model(project_report),object_id=project_report.id)
        if answer_obj and (sub.qtype == 'T' or sub.qtype == 'APT' or sub.qtype == 'ck'):# if answer_obj is there get answers according to the question type
            data['answer']= answer_obj.text 
        elif answer_obj and answer_obj.attachment_file :
            data['answer']=answer_obj.attachment_file.url
        else: # else get the answers from the details dictionary 
            data = get_org_logos(data,project,keys,details,sub)# to get the organozation logos and the answers from details dictionary
           
        sub_quest_list.append(data)
    return sub_quest_list
    
def get_org_logos(data,project,keys,details,sub):
    #get the organization logos
    from projectmanagement.templatetags import urs_tags
    org_logo,ngo_logo = urs_tags.get_org_logo(project)
    if data.get('q_name') == 'logos': 
        if ngo_logo:
            data['answer'] = ngo_logo
        else :
            data['answer'] = ""
    if data.get('q_name')== 'client_logo' :
        if org_logo:
            data['answer'] = org_logo
        else :
            data['answer'] = ""
    if data.get('q_name') == 'pmo_logo':
        data['answer'] = "/static/img/new-logo.png"
    # get the answers from details if there is no answer object ..
    if sub.slug in keys:
        data['answer'] = details[sub.slug]
    return data
    
@register.assignment_tag 
def get_gantt_details(v,projectobj):
# this function to get the gantt chart details for the particular quarter that is generated
    start_date = v.split('to')[0].rstrip()
    end_date = v.split('to')[1].lstrip()
    start_date = datetime.strptime(start_date[:19], '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date[:19], '%Y-%m-%d').date()
    import json
    data = {'project_id':int(projectobj.id),'start_date':start_date,'end_date':end_date}
    rdd = requests.get(PMU_URL +'/managing/gantt-chart-data/', data=data)
    taskdict = ast.literal_eval(json.dumps(rdd.content))
    return taskdict

@register.assignment_tag     
def get_report_quarters(report_type,start_date,end_date,budget_quarters):
    month_dict = {1:'January',2:'February',3:'March',4:'April',5:'May',
                      6:'June',7:'July',8:'August',9:'September',
                      10:'October',11:'November',12:'December'}
    report_duration=quarter_duration=''
    if report_type == 1:
        end_date = end_date.replace(tzinfo=pytz.utc)
        conver_time = end_date.astimezone(pytz.timezone('Asia/Kolkata'))
        for k in budget_quarters.keys():
            value = budget_quarters[k].split(' to ')[-1]
            if value == conver_time.strftime('%Y-%m-%d'):
                report_duration = int(k)+1
                quarter_duration = budget_quarters[k]
    else:
        report_date = start_date.replace(tzinfo=pytz.utc)
        conver_time = report_date.astimezone(pytz.timezone('Asia/Kolkata'))
        month = month_dict.get(conver_time.month)
        year = conver_time.year
        report_duration = month+' '+str(year)
        quarter_duration=str(start_date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d'))+' to '+str(end_date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d'))
    return report_duration,quarter_duration
    
@register.assignment_tag
def get_converted_time(created):
    created_time = created.replace(tzinfo=pytz.utc)
    convert_time = created_time.astimezone(pytz.timezone('Asia/Kolkata'))
    time = convert_time.strftime("%I:%M %p")
    return time
    
@register.assignment_tag
def get_from_to_dates(date):
    start_date =end_date=''
    date_list=[]
    try:
        date_list = date.split(' TO ')
        if date_list:
            start_date = date_list[0]
            end_date = date_list[1]
    except:
        pass
    return start_date,end_date

@register.assignment_tag
def get_quarter_names(key,number_dict):
    name=''
    name = number_dict.get(key)
    return name

@register.assignment_tag
def get_month_name(date):
    from datetime import datetime
    month_name = date.split(' to ')[0]
    month_name = datetime.strptime(month_name, '%Y-%m-%d')
    month_name = month_name.strftime("%B")
    return month_name

@register.assignment_tag
def get_images(obj):
    obj = obj
    attachment = Attachment.objects.filter(object_id=obj.id,content_type=ContentType.objects.get(model='Project')).order_by('-created')
    image = PMU_URL
    return attachment

@register.assignment_tag
def get_taskcompletion(obj):
    total_tasks = completed_tasks = total_milestones = 0
    milestones = []
    project = obj
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
    return percent

@register.assignment_tag
def get_parameter_type(obj):
    for i in obj:
        if i.keyparameter.parameter_type == 'NUM' or i.keyparameter.parameter_type == 'CUR':
            pie_chart = 0
        else:
            pie_chart = 1
    return pie_chart
 
@register.assignment_tag    
def get_block_tab_removed(questions,block_type,report_obj):
    tab_removed = ''
    removed_id = ''
    remove_obj=RemoveQuestion.objects.get_or_none(quarter_report= report_obj,block_type=block_type)
    if remove_obj:
        removed_list = literal_eval(remove_obj.text)
        remove_id = remove_obj.id if str(remove_obj.text) != '[]' else ''
        if set(removed_list) == set(questions):
            tab_removed = 'true'
        else:
            tab_removed = 'false'
    else:
        tab_removed = 'false'
        remove_id = ''
    return tab_removed,remove_id
    
from calendar import monthrange
@register.assignment_tag   
def get_monthly_date(period):
    month_dict = {'January':1,'February':2,'March':3,'April':4,'May':5,
                      'June':6,'July':7,'August':8,'September':9,
                      'October':10,'November':11,'December':12}
    year = int(period.split(' ')[1])
    mnth = period.split(' ')[0]
    month = month_dict.get(mnth)
    days = monthrange(year, month)[1]
    start_date = str(year)+"-"+str(month)+"-"+str(1)
    end_date = str(year)+"-"+str(month)+"-"+str(days)
    period = start_date+' to '+ end_date
    return period

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

import json
@register.assignment_tag
def taskdict_json(taskdict):
    taskdict = json.loads(taskdict)
    return taskdict

def string_trim(string):
    # import ipdb; ipdb.set_trace()
    file_extension = string.split('.')
    if len(string) > 19:
        new_string = string[:25] + '...' + file_extension[0][-6:] + '.'+file_extension[-1]
    else:
        new_string = string
    return new_string

def read_more_text(text):
    if len(text) > 50:
        short_text = text[:190]
        more_text = text[50:]
    else:
        short_text = text
        more_text = ''
    return short_text,more_text

def get_attachment_type(file_name):
    image_format = ['tif', 'tiff', 'gif', 'jpeg', 'jpg', 'jif', 'jfif', 'jp2', 'jpx', 'j2k', 'j2c ', 'fpx', 'pcd', 'png']
    docs_format = ['rtf', 'odt', 'docx', 'pot', 'pxt', 'txt', 'odf', 'doc']
    file_extension = file_name.split('.')[-1]
    if file_extension in image_format:
        attachment_file_type = 'image'
    else:
        attachment_file_type = 'doc'
    return attachment_file_type