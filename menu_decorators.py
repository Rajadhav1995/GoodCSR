# Custom Decorators defines here
from django.utils.decorators import method_decorator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import logout
from userprofile.models import *
from django.views.decorators.http import require_POST as post_only
import urllib
from views.login import signin
from projectmanagement.templatetags.urs_tags import userprojectlist

def check_loggedin_access(view):
    def is_auth(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        next = request.GET.get('next')
        keys = ['summary','updates','task-milestone','budget','files','tranches','projecttasks','generate-report']
        if user_id:
            key = request.GET.get('key')
            project_slug = str(request.GET.get('slug'))
            user_obj = UserProfile.objects.get(user_reference_id = user_id )
            obj_list = userprojectlist(user_obj)
            get_project_slug_list = obj_list.values_list("slug",flat=True)
            if project_slug in get_project_slug_list or key not in keys:
                user = signin(request)
            else:
                message = "Permission Denined!!!Please Contact Administrator."
                return render(request, 'login.html', locals())
        elif request.method == 'POST':
            user = signin(request)
        elif user_id == '':
            message = "Permission Denined!!!Please login with credentials."
            return render(request, 'login.html', locals())
        return view(request, *args, **kwargs)
    return is_auth



