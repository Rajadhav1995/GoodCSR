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
from pmu.settings import RECAPTCHA_PUBLIC_KEY
# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
def check_loggedin_access(view):
    def is_auth(request, *args, **kwargs):
        cpatcha_public_key = RECAPTCHA_PUBLIC_KEY
        user_id = request.session.get('user_id')
        if not user_id:
            user_id=request.GET.get('has')
        next = request.GET.get('next')
        keys = ['summary','updates','task-milestone','budget','files','tranches','projecttasks','generate-report']
        if user_id:
            key = request.GET.get('key')
            project_slug = request.GET.get('slug') or request.POST.get('slug')
            user_obj = UserProfile.objects.get_or_none(user_reference_id = user_id )
            if user_obj:
                obj_list = userprojectlist(user_obj)
                get_project_slug_list = obj_list.values_list("slug",flat=True)
                #if project_slug in get_project_slug_list or key not in keys:
                if str(project_slug) in get_project_slug_list or request.path == '/dashboard/' or request.GET.get('status') in ['0','2']:
                    user = signin(request)
                else:
                    message = "Permission Denined!!!Please Contact Administrator."
                    return render(request, 'login.html', locals())
            else:
                message = "Permission Denined!!!Please Contact Administrator."
                return render(request, 'login.html', locals())
        elif request.method == 'POST':
            user = signin(request)
        elif user_id == '' or user_id == None :
            message = "Permission Denined!!!Please login with credentials."
            return render(request, 'login.html', locals())
        return view(request, *args, **kwargs)
    return is_auth
# allows you to hit your target and reach your goal. 
#By setting goals for yourself you are able to measure your progress 
#because you always have a fixed endpoint or benchmark to compare with. 
#Take this scenario for example: David makes a goal to write a book with
# a minimum of 300 pages. He starts writing every day and works really 
# hard but along the way, he loses track of how many more pages he has 
# written and how much more he needs to write. 
#So rather than panicking David simply counts the number of pages he has 
#already written and he instantly determines his progress and knows how much 
#further he needs to go. allows you to hit your target and reach your goal. 
#By setting goals for yourself you are able to measure your progress because
# you always have a fixed endpoint or benchmark to compare with. Take this 
# scenario for example: David makes a goal to write a book with a minimum of
#  300 pages. He starts writing every day and works really hard but along the 
#  way, he loses track of how many more pages he has written and how much more 
#  he needs to write. 
#So rather than panicking David simply counts the number of pages he has already
# written and he instantly determines his progress and knows how much further he
#  needs to go. allows you to hit your target and reach your goal. 
#By setting goals for yourself you are able to measure your progress because you
# always have a fixed endpoint or benchmark to compare with. Take this scenario 
# for example: David makes a goal to write a book with a minimum of 300 pages.
#  He starts writing every day and works really hard but along the way,
#   he loses track of how many more pages he has written and how much more he needs to write. 
#So rather than panicking David simply counts the number of pages he has 
#already written and he instantly determines his progress and knows how much 
#further he needs to go. allows you to hit your target and reach your goal. 
#By setting goals for yourself you are able to measure your progress because 
#you always have a fixed endpoint or benchmark to compare with. Take this 
#scenario for example: David makes a goal to write a book with a minimum of 
#300 pages. He starts writing every day and works really hard but along the 
#way, he loses track of how many more pages he has written and how much more 
#he needs to write. 
#So rather than panicking David simply counts the number of pages he has 
#already written and he instantly determines his progress and knows how much 
#further he needs to go.
