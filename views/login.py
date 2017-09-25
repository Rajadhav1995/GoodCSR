import requests
import json
from django.shortcuts import render
from django.contrib.auth.models import User
from  django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from pmu.settings import (SAMITHA_URL,)
from projectmanagement.models import UserProfile
from media.models import Section,Article

def signin(request):
#    if request.session.get('user_id') or request.session.get('user_id') != '':
#        if next:
#            return HttpResponseRedirect(next)
#        else:
#            return HttpResponseRedirect('/dashboard/')
    
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
    session = request.session.get('user_id')
    request.session['user_id'] = ''
    return HttpResponseRedirect('/')

def homepage(request):
    banner_images = Section.objects.filter(article__slug='banner-images')
    features = Section.objects.filter(article__slug='features')
    midpart_image = Section.objects.filter(article__slug='midpart')
    capacity = Section.objects.get_or_none(article__slug='capacity-building')
    return render(request,'home_page.html', locals())
