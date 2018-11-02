import requests
import json
from django.shortcuts import render
from django.contrib.auth.models import User
from  django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from pmu.settings import (SAMITHA_URL,RECAPTCHA_PUBLIC_KEY)
from projectmanagement.models import UserProfile
from media.models import Section,Article
from django.core.cache import cache
import urllib3
import simplejson as json
from django.contrib import messages
from rest_framework.views import APIView,Response
from pmu.settings import NOCAPTCHA
def signin(request):
    # this function is for
    # login from goodcsr db
    #if request.GET.get('message'):
     #   message = request.GET.get('message')
    #if request.GET.get('cpatcha_msg'):
     #   cpatcha_msg = request.GET.get('cpatcha_msg')
    cpatcha_public_key = RECAPTCHA_PUBLIC_KEY
    if request.session.get('user_id'):
        return HttpResponseRedirect('/dashboard/')
    if request.method == 'POST':
        if request.POST.get('g-recaptcha-response') or NOCAPTCHA:
            next = request.POST.get('next')
            data = {'username':request.POST.get('username'), 'password':request.POST.get('password')}
            headers = {'content-type': 'application/json'}
            try:
#            http = urllib3.PoolManager()
#            r = http.request('POST',SAMITHA_URL + '/pmu/login/', fields = data)
                response = requests.post(SAMITHA_URL + '/pmu/login/', json.dumps(data),headers=headers)
            except requests.exceptions.ConnectionError:
                status_code = "Connection refused"
        #validation_data = json.loads(response.data)
            validation_data = response.json()
#        userobj = UserProfile.objects.get_or_none(email=str(request.POST.get('username')))
#        validation_data = {'status':2,'user_id':int(userobj.user_reference_id) if userobj else ''}
            if validation_data.get('status') == "2":
                request.session['user_id'] = int(validation_data.get('user_id'))
                if next:
                    return HttpResponseRedirect(next)
                else:
                    return HttpResponseRedirect('/dashboard/')
            else:
                mess = validation_data.get('msg')
                messages.add_message(request, messages.INFO, mess)
                return HttpResponseRedirect('/intermidate-login/')
        else:
            mess = 'Invalid Captcha! Please try again'
            messages.add_message(request, messages.INFO, mess)
            return HttpResponseRedirect('/intermidate-login/')
    return render(request, 'login.html', locals())


# introduce intermidate login page (back and refresh)
def intermidate_login(request):
    return HttpResponseRedirect('/login/')

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

class PMULoginAPI(APIView):
    #this function is for login through the PMU db as a standalone
    def post(self, request, *args, **kwargs):
        """
        User Login.
        ---
        parameters:
        - name: username
          description: Username Login
          required: true
          type: string
          paramType: form
        - name: password
          description: Password for Login
          paramType: form
          required: true
          type: string
        """
        print 'PMULogin API'
        response = {}
        data = request.data
        user = authenticate(username = data.get('username'), password = data.get('password'))
        if user is not None:
            if user.is_active:
                response.update({"status":"2","msg":"User Logged-in Succesfully",
                                "user_id":int(user.id)})
            else:
                #response.update({"status":"0","msg":"User is inactive"})
                response.update({"status":"0","msg":"Invalid Credentials"})
        else:
            #response.update({"status":"0","msg":"Username/Password mismatch"})
            response.update({"status":"0","msg":"Invalid Credentials"})
        return Response(response)