from django import template
register = template.Library()
from datetime import datetime
from media.models import Comment
from django.contrib.contenttypes.models import ContentType
import pytz
from taskmanagement.models import Task

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
    
