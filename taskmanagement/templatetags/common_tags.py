from django import template
register = template.Library()

@register.assignment_tag
def get_details(obj):
    closed_task = update = ''
    formats = '%H:%M %p'
    user = obj.get('user_name')
    task_name = obj.get('task_name')
    project = obj.get('project_name')
    time= obj.get('time').strftime(formats)
    date = obj.get('date')
    description = obj.get('attach')
    task_status = obj.get('task_status')
    if task_status.status == 2:
        closed_task = user + ''' completed <u>'''+ task_name + project + '''</u> <span>'''+ str(time) + '''</span>'''
    update = user + ''' uploaded <u>'''+ description +'''</u> in <u> '''+ project + '''</u> <span>'''+ str(time) + '''</span>'''
    return update 
    
    
