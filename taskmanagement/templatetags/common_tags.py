from django import template
register = template.Library()
from datetime import datetime
from media.models import Comment,Attachment
from django.contrib.contenttypes.models import ContentType
import pytz
from taskmanagement.models import Task
from budgetmanagement.models import *
from projectmanagement.models import Project,UserProfile,ProjectFunderRelation,ProjectParameter

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
    questions = Question.objects.filter(block=block,parent=None)
    for i in questions:
        question_dict = {'q_id':i.id,'q_text':i.text,
            'q_type':i.qtype,'q_name':i.slug}
        question_list.append(question_dict)
    return question_list
    
    
@register.assignment_tag 
def get_auto_populated_questions(ques_id,project,project_report):
    # to get the auto populated questions that are tagged to that particular section
    data = {}
    question = Question.objects.get_or_none(id=ques_id)
    sub_quest_list = []
    sub_questions = Question.objects.filter(parent = question)
    mapping_view = ProjectFunderRelation.objects.get_or_none(project=project)
    cover_image = Attachment.objects.get_or_none(description__iexact = "cover image",attachment_type = 1,
            content_type = ContentType.objects.get_for_model(project_report),
            object_id = project_report.id)
    details = {'report_type':project_report.get_report_type_display(),
        'report_duration':project_report.start_date.strftime('%Y-%m-%d')+' TO '+project_report.end_date.strftime('%Y-%m-%d'),'prepared_by':project_report.created_by.name,'client_name':mapping_view.funder.organization,
        'report_name': project_report.name if project_report.name else '',
        'cover_image': cover_image.attachment.url if cover_image else '',
        'project_title':project.name,'project_budget':project.total_budget,
        'donor':mapping_view.funder.organization,
        'implement_ngo':mapping_view.implementation_partner.organization,
        'no_of_beneficiaries':project.no_of_beneficiaries,'project_duration':project.start_date.strftime('%Y-%m-%d')+' TO '+project.end_date.strftime('%Y-%m-%d')}
    keys = details.keys()
    for sub in sub_questions:
        data = {'q_id':sub.id,'q_text':sub.text,'q_type':sub.qtype,'q_name':sub.slug}
        if data.get('q_name') == 'logos':
            from projectmanagement.templatetags import urs_tags
            org_logo = urs_tags.get_org_logo(project)
            if org_logo:
                data['answer'] = org_logo
            else :
                data['answer'] = "/static/img/GoodCSR_color_circle.png"
        if data.get('q_name') in keys:
            data['answer'] = details[data.get('q_name')]
        sub_quest_list.append(data)
    print sub_quest_list
    return sub_quest_list
    
