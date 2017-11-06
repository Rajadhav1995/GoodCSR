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

@register.assignment_tag
def get_details(obj):
    closed_tasks = update = ''
    formats = '%I:%M %p'
    if obj:
        user = obj.get('user_name') or ''
        task_name = obj.get('task_name') or ''
        project = obj.get('project_name') or ''
#        time_zone= obj.get('time').replace(tzinfo = pytz.utc) if obj.get('time') else ''
#        convert_time = time_zone.astimezone(pytz.timezone('Asia/Kolkata'))
#        time = convert_time.strftime(formats)
        time = obj.get('time').time().strftime(formats) if obj.get('time') else ''
        date = obj.get('date').strftime('%d %B %Y') if obj.get('date') else ''
        description = obj.get('attach') or ''
        task_status = obj.get('task_status') or ''
        if task_status and task_status.status == 2:
            closed_tasks = '''<li><img src="/static/img/default_profile_image.png" class="user-image" alt="User Image"> <div class="update-pad">'''+user + ''' completed <u>'''+ task_name + ' - ' + project + '''</u> <span>'''+ str(date)+' '+ str(time) + '''</span></div></li>'''
        update = '''<li><img src="/static/img/default_profile_image.png" class="user-image" alt="User Image"> <div class="update-pad">'''+user + ''' uploaded <u>'''+ ''' image '''+'''</u> in <u> '''+ project + '''</u> <span>'''+ str(date)+' '+str(time) + '''</span></div></li>'''
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
def get_questions(block,project_report):
    # to get the questions that are tagged in that particular section
    question_list = []
    question_dict={} 
    report_obj=ProjectReport.objects.get_or_none(id=project_report.id)
    questions = Question.objects.filter(block=block,parent=None,block__block_type=0)
    for i in questions:
        answer = Answer.objects.get_or_none(question = i,content_type=ContentType.objects.get_for_model(report_obj),object_id=report_obj.id)
        question_dict = {'q_id':i.id,'q_text':i.text,
            'q_type':i.qtype,'q_name':i.slug}
        if answer and (i.qtype == 'T' or i.qtype == 'ck'):
            question_dict['answer'] = answer.text 
        elif i.qtype == 'F':
            question_dict['answer'] = answer.attachment_file.url if answer and answer.attachment_file else "/static/img/GoodCSR_color_circle.png"
        question_list.append(question_dict)
    return question_list
    
    
@register.assignment_tag 
def get_auto_populated_questions(ques_id,project,project_report):
    # to get the auto populated questions that are tagged to that particular section
    data = {}
    question = Question.objects.get_or_none(id=ques_id)
    sub_quest_list = []
    sub_questions = Question.objects.filter(parent = question,block__block_type=0)
    mapping_view = ProjectFunderRelation.objects.get_or_none(project=project)
    cover_image = Attachment.objects.get_or_none(description__iexact = "cover image",attachment_type = 1,
            content_type = ContentType.objects.get_for_model(project_report),
            object_id = project_report.id)
    # details dict is to get the details of two sections on first click of generate report
    details = {'report_type':project_report.get_report_type_display(),
        'report_duration':project_report.start_date.strftime('%Y-%m-%d')+' TO '+project_report.end_date.strftime('%Y-%m-%d'),
        'prepared_by':project_report.created_by.attrs.get('first_name')+' '+project_report.created_by.attrs.get('last_name'),'client_name':mapping_view.funder.organization,
        'report_name': project_report.name if project_report.name else '',
        'cover_image': cover_image.attachment_file.url if cover_image else '',
        'project_title':project.name,'project_budget':project.total_budget,
        'donor':mapping_view.funder.organization,
        'implement_ngo':mapping_view.implementation_partner.organization,
        'no_of_beneficiaries':project.no_of_beneficiaries,'project_duration':project.start_date.strftime('%Y-%m-%d')+' TO '+project.end_date.strftime('%Y-%m-%d'),
        'location':project.get_locations()}
    # to get the answers of auto populated questions 
    sub_quest_list = get_sub_answers(details,sub_questions,project_report,project)
    return sub_quest_list
    
@register.assignment_tag 
def get_milestones(quarter,report_obj,type_id):
# to get the milestones or activities that are save for particular quarters
    report_miles = []
    data = {}
    sss = {1:'milestone-setion',2:'activity-section'}
    question = Question.objects.get_or_none(slug=sss.get(type_id))
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
        answer_obj = Answer.objects.get_or_none(question=sub,content_type=ContentType.objects.get_for_model(project_report),object_id=project_report.id)
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
    if data.get('q_name') == 'logos' or data.get('q_name')== 'client_logo' or data.get('q_name') == 'pmo_logo':
        from projectmanagement.templatetags import urs_tags
        org_logo = urs_tags.get_org_logo(project)
        if org_logo:
            data['answer'] = org_logo
        else :
            data['answer'] = "/static/img/GoodCSR_color_circle.png"
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
def get_report_quarters(start_date,end_date,budget_quarters):
    report_duration=0
    for k in budget_quarters.keys():
        try:
            value = budget_quarters[k].split(' to ')[-1]
        except:
            value = ''
        if value == end_date.strftime('%Y-%m-%d'):
            report_duration = int(k)+1
    return report_duration
