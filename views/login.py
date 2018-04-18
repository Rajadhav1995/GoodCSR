import requests
import json
from django.shortcuts import render
from django.contrib.auth.models import User
from  django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from pmu.settings import (SAMITHA_URL,)
from projectmanagement.models import UserProfile
from media.models import Section,Article
from django.core.cache import cache

def signin(request):
    # this function is for
    # login from goodcsr db
    if request.session.get('user_id'):
        return HttpResponseRedirect('/dashboard/')
    if request.method == 'POST':
        next = request.POST.get('next')
        data = {'username':request.POST.get('username'), 'password':request.POST.get('password')}
        try:
            r = requests.post(SAMITHA_URL + '/pmu/login/', data=data)
        except requests.exceptions.ConnectionError:
            status_code = "Connection refused"
        validation_data = json.loads(r.content)
#        userobj = UserProfile.objects.get_or_none(email=str(request.POST.get('username')))
#        validation_data = {'status':2,'user_id':int(userobj.user_reference_id) if userobj else ''}
        if validation_data.get('status') == 2:
            request.session['user_id'] = validation_data.get('user_id')
            if next:
                return HttpResponseRedirect(next)
            else:
                return HttpResponseRedirect('/dashboard/')
        else:
            message = validation_data.get('msg')
    
    return render(request, 'login.html', locals())


def signout(request):
    # this function is for 
    # user session logout
    # 
    request.session['user_id'] = ''
    for key in request.session.keys():
        del request.session[key]
    return HttpResponseRedirect('/')

def homepage(request):
    # # this function is for 
    # showing dynamic homepage 
    # 
    if request.session.get('user_id'):
        return HttpResponseRedirect('/dashboard/')
    banner_images = Section.objects.filter(article__slug='banner-images', active=2)
    features = Section.objects.filter(article__slug='features')
    midpart_image = Section.objects.filter(article__slug='midpart')
    capacity = Section.objects.get_or_none(article__slug='capacity-building')
    return render(request,'homepage/home_page.html', locals())

def login_popup(request):
    # this function is for 
    # showing login popup
    # 
    # function NOT IN USE
    return render(request,'homepage/login_popup.html',locals())


# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
def get_image():
    import matplotlib.pyplot as plt
 
# Data to plot
    labels = 'Python', 'C++', 'Ruby', 'Java'
    sizes = [215, 130, 245, 210]
    colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue']
    explode = (0.1, 0, 0, 0)  # explode 1st slice

    import os

    script_dir = os.path.dirname(__file__)
    results_dir = os.path.join(script_dir, 'Results/')
    sample_file_name = "sample"

    if not os.path.isdir(results_dir):
        os.makedirs(results_dir)
    # Plot
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=140)
     
    plt.axis('equal')
    plt.savefig(results_dir + sample_file_name)

# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
