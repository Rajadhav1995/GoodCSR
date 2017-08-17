from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse,HttpResponseRedirect
from pmu.settings import BASE_DIR
from taskmanagement.models import *
from taskmanagement.forms import ActivityForm
# Create your views here.

def listing(request,model_name):
    model = ContentType.objects.get(model = model_name)
    obj_list = model.model_class().objects.all()
    return render(request,'listing.html',locals())
    

def add_taskmanagement(request,model_name,m_form):
    form=eval(m_form)
    if request.method=='POST':
        form=form(request.POST,request.FILES)
        if form.is_valid():
            f=form.save() 
            if model_name == 'activity' or model_name == 'task':
                f.slug = f.name.replace(' ','-')
                f.save()
    else:
        form=form()
    return render(request,'taskmanagement/forms.html',locals())
    
def edit_taskmanagement(request,model_name,m_form,slug):
    form=eval(m_form)
    m=eval(model_name).objects.get(slug = slug)
    if request.method == 'POST':
        form=form(request.POST,request.FILES,instance=m)
        if form.is_valid():
            f=form.save()
            if model_name == 'activity' or model_name == 'task':
                f.slug = f.name.replace(' ','-')
                f.save()
    else:
        form=form(instance=m)
    return render(request,'taskmanagement/forms.html',locals())

