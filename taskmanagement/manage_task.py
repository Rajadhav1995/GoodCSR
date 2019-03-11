from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from taskmanagement.models import *
from rest_framework.response import Response
from menu_decorators import check_loggedin_access

@check_loggedin_access
def remove_task(request):
	url=request.META.get('HTTP_REFERER')
        from django.apps import apps
	data={'Project':'projectmanagement','Task':'taskmanagement',
              'Budget':'budgetmanagement','Userprofile':'userprofile',
              'Media':'media','Activity':'taskmanagement',
               'Milestone':'taskmanagement','Tranche':'budgetmanagement'}
	app_label=data.get(request.GET.get(str('model')))
	model = apps.get_model(app_label,request.GET.get(str('model')))
		
	if request.GET.get('model') == 'Task':
		obj = model.objects.get(slug=request.GET.get('name'))
		obj.active = 0
		obj.save()
		milestone = Milestone.objects.filter(task=obj)
		for j in milestone:
			j.active = 0
			j.save()
	elif request.GET.get('model') == 'Activity':
		obj = model.objects.get(slug=request.GET.get('name'))
		obj.active = 0
		obj.save()
		activity = Task.objects.filter(activity=obj)
		for i in activity:
			i.active = 0
			i.save()
			milestone = Milestone.objects.filter(task=i)
			for k in milestone:
				k.active = 0
				k.save()
	else:
		obj = model.objects.get(slug=request.GET.get('name'))
		obj.active = 0
		obj.save()
	return HttpResponseRedirect(url)


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
# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast. 
