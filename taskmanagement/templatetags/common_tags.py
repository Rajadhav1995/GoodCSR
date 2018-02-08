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
from pmu.settings import PMU_URL
from ast import literal_eval
from itertools import chain

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

@register.assignment_tag   
def task_comments_progress(date,task_id):
    task_data = []
    print "aditya",task_id
    # comment_list = Comment.objects.filter(active=2,content_type=ContentType.objects.get(model=('task')),object_id=task_id).order_by('-id')
    # for i in comment_list.filter(created__range = (datetime.combine(date, datetime.min.time()),datetime.combine(date, datetime.max.time()))):
    #     data = {'name':i.created_by.attrs,'comment_text':i.text,'time':i.created}
        # task_data.append(data)
    task_progress = Task.objects.get(id=task_id)
    task_progress_history = task_progress.history.filter(modified__range = (datetime.combine(date, datetime.min.time()),datetime.combine(date, datetime.max.time())))
    for i in task_progress_history:
        if i.task_progress:
            previous_task_progress = i.get_previous_by_created().task_progress
            # if i.task_progress != i.get_previous_by_created().task_progress:
            cell_one = {'name':'','comment_text':'','time':i.modified,
                        'task_progress':i.task_progress,
                        'previous_task_progress':i.get_previous_by_created().task_progress if i.get_previous_by_created().task_progress!=None else 0,}
            task_data.append(cell_one)
    task_data.sort(key=lambda item:item['time'], reverse=True)
    return task_data

from datetime import date
@register.assignment_tag
def get_task_comments(comment_date,task_id):
    comment_data = {}
    new_date = comment_date.replace(microsecond=0)
    comment_list = Comment.objects.get_or_none(active=2,content_type=ContentType.objects.get(model=('task')),object_id=task_id,\
            created__year=new_date.year,created__month=new_date.month,created__day=new_date.day,created__hour=new_date.hour,created__minute=new_date.minute,created__second=new_date.second)
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