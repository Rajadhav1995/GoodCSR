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

def feedback(request):
    form = ContactPersonForm()
    if request.method=='POST':
        form = ContactPersonForm(request.POST)
        email = request.POST.get('email')
        # email_list = [i.email for i in ContactPersonInformation.objects.all()]
        # if email in email_list:
            # messages.error(request, 'You have already requested for demo. Our executive will contact you soon ')
            # return HttpResponseRedirect('/feedback/')
        if form.is_valid():
            obj = form.save()
            obj.save()
            html_message = loader.render_to_string(
                      BASE_DIR+'/templates/homepage/send_program.html',
                      {
                          'full_name': obj.name,
                       })
            send_mail('Samhita GoodCSRs Project Management Module- DEMO','', 'care@goodcsr.in', [obj.email],html_message=html_message)

            html_message = loader.render_to_string(
                      BASE_DIR+'/templates/homepage/email_template_admin.html',
                      {
                          'fname': obj.name,
                          'email': obj.email,
                          'mobile': obj.mobile_number,
                          'org_name' : obj.organization_name,
                          'msg': obj.message,
                       })
            send_mail('Request for PMU DEMO','', 'care@goodcsr.in', ['care@goodcsr.in', 'jagpreet.p@samhita.org', 'anirudhan.t@collectivegood.in', 'shahzarin@goodcsr.in', 'namrata@goodcsr.in' ],html_message=html_message)
            messages.success(request, "Thank you for expressing interest in Samhita GoodCSR's Project Management Module. Our project management consultant will get in touch with you shortly.")
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
