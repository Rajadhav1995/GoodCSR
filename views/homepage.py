import requests,ast
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from media.models import Article,Section,ContactPersonInformation
from media.forms import ContactPersonForm
from django.template import loader
from pmu.settings import BASE_DIR
from django.contrib import messages
from django.core.mail import send_mail

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
    form = ContactPersonForm()
    if request.method=='POST':
        form = ContactPersonForm(request.POST)
        email = request.POST.get('email')
        email_list = [i.email for i in ContactPersonInformation.objects.all()]
        if email in email_list:
            messages.error(request, 'You have already requested for demo. Our executive will contact you soon ')
            return HttpResponseRedirect('/feedback/')
        if form.is_valid():
            obj = form.save()
            obj.save()
            html_message = loader.render_to_string(
                      BASE_DIR+'/templates/homepage/send_program.html',
                      {
                          'full_name': obj.name,
                       })
            send_mail('Samhita GoodCSRs Project Management Module- DEMO','', 'adityanraut@gmail.com', ['aditya.raut@mahiti.org'],html_message=html_message)

            html_message = loader.render_to_string(
                      BASE_DIR+'/templates/homepage/email_template_admin.html',
                      {
                          'fname': obj.name,
                          'email': obj.email,
                          'mobile': obj.mobile_number,
                          'org_name' : obj.organization_name,
                          'msg': obj.message,
                       })
            send_mail('Request for PMU DEMO','', 'adityanraut@gmail.com', ['aditya.raut@mahiti.org'],html_message=html_message)

            messages.success(request, 'Thank you for Requesting Demo')
            return HttpResponseRedirect('/feedback/')
    return render(request,'homepage/feedback.html',locals())

from django.http import JsonResponse
def email_validation(request):
    email = request.GET.get('uname', None)
    print "aditya"
    data = {
        'is_taken': ContactPersonInformation.objects.filter(email__iexact=email).exists()
    }
    return JsonResponse(data)
