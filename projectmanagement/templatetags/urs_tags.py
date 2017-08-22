from django import template
from django.contrib.auth.models import User
from projectmanagement.models import (Project, UserProfile)

register = template.Library()

@register.assignment_tag
def get_user_project(request):
    user_id = request.session.get('user_id')
    user_obj = UserProfile.objects.get(user_reference_id = user_id )
    obj_list = Project.objects.filter(created_by = user_obj)
    project_count = obj_list.count()
    return obj_list


