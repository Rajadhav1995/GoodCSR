from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse,HttpResponseRedirect
from pmu.settings import BASE_DIR
# Create your views here.

def listing(request,model_name):

    obj = eval(model_name).objects.all().order_by('-id')
    return render(request,'listing.html',locals())
    



