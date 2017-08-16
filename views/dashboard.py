from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse,HttpResponseRedirect

#create views of dashboard

def admin_dashboard(request):
    return render(request,'base.html')
    
    
