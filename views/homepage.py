import requests,ast
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from media.models import Article,Section

def add_section(request):
    key=''
    slug =  request.GET.get('slug')
    try:
        project = Project.objects.get(slug = request.GET.get('slug'))
    except:
        project = Project.objects.get(slug= request.POST.get('slug_project'))
    user_id = request.session.get('user_id')
    user = UserProfile.objects.get_or_none(user_reference_id = user_id)
    budget = Budget.objects.get_or_none(project = project,active=2)
    form=eval(m_form)
    if budget:
        if request.method=='POST':
            form=form(user_id,project.id,request.POST,request.FILES)
            if form.is_valid():
                f=form.save()
                from projectmanagement.common_method import unique_slug_generator
                f.slug = f.name.replace(' ','-')
                f.save()
                if model_name == 'Activity' or model_name == 'Task':
                    f.created_by = user
                    f.save()
                    return HttpResponseRedirect('/managing/listing/?slug='+project.slug)
                else :
                    return HttpResponseRedirect('/managing/listing/?slug='+project.slug)
        else:
            form=form(user_id,project.id)
    else:
        message = "Budget is not added"
    return render(request,'taskmanagement/base_forms.html',locals())

def feedback(request):
    return render(request,'feedback.html',locals())