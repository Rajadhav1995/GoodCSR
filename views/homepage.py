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

# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
def feedback(request):
    # this function is to save and edit feedback form
    # in homepage
    # 
    form = ContactPersonForm()
    if request.method=='POST':
        form = ContactPersonForm(request.POST)
        email = request.POST.get('email')
        if form.is_valid():
            obj = form.save()
            obj.save()
            # sending email to user who given feedback
            html_message = loader.render_to_string(
                      BASE_DIR+'/templates/homepage/send_program.html',
                      {
                          'full_name': obj.name,
                       })
            send_mail('Samhita GoodCSRs Project Management Module- DEMO','', 'care@goodcsr.in', [obj.email],html_message=html_message)
            # sending email to admin 
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
    # this function is to validate email 
    # 
    email = request.GET.get('uname', None)
    data = {
        'is_taken': ContactPersonInformation.objects.filter(email__iexact=email).exists()
    }
    return JsonResponse(data)

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