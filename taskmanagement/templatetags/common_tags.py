from django import template
register = template.Library()
from datetime import datetime

@register.assignment_tag
def get_details(obj):
    closed_tasks = update = ''
    formats = '%H:%M %p'
    user = obj.get('user_name') or ''
    task_name = obj.get('task_name') or ''
    project = obj.get('project_name') or ''
    time= obj.get('time').strftime(formats) if obj.get('time') else ''
    date = obj.get('date').strftime('%d %B %Y') if obj.get('time') else ''
    description = obj.get('attach') or ''
    task_status = obj.get('task_status') or ''
    if task_status and task_status.status == 2:
        closed_tasks = '''<li><img src="/static/img/avatar.jpg" class="user-image" alt="User Image"> <div class="update-pad">'''+user + ''' completed <u>'''+ task_name + ' - ' + project + '''</u> <span>'''+ str(date)+' '+ str(time) + '''</span></div></li>'''
    update = '''<li><img src="/static/img/avatar.jpg" class="user-image" alt="User Image"> <div class="update-pad">'''+user + ''' uploaded <u>'''+ description +'''</u> in <u> '''+ project + '''</u> <span>'''+ str(date)+' '+str(time) + '''</span></div></li>'''
    return update,closed_tasks 
    
    
