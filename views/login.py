import requests
import json
from django.shortcuts import render
from django.contrib.auth.models import User
from  django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from pmu.settings import (SAMITHA_URL,)

def signin(request):
    next = request.GET.get('next')
#    if request.session.get('user_id') or request.session.get('user_id') != '':
#        if next:
#            return HttpResponseRedirect(next)
#        else:
#            return HttpResponseRedirect('/dashboard/')
    if request.method == 'POST':
        data = {'username':request.POST.get('username'), 'password':request.POST.get('password')}
        try:
            r = requests.post(SAMITHA_URL + '/pmu/login/', data=data)
        except requests.exceptions.ConnectionError:
            r.status_code = "Connection refused"
        validation_data = json.loads(r.content)
        if validation_data.get('status') == 2:
#            login(request, user)
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
