from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from taskmanagement.models import *
from rest_framework.response import Response


def remove_task(request):
	url=request.META.get('HTTP_REFERER')
	
	model_name = eval(request.GET.get('model'))
	
	if request.GET.get('model') == 'Task':
		obj = model_name.objects.get(slug=request.GET.get('name'))
		obj.active = 0
		obj.save()
		milestone = Milestone.objects.filter(task=obj)
		for j in milestone:
			j.active = 0
			j.save()
	elif request.GET.get('model') == 'Activity':
		obj = model_name.objects.get(slug=request.GET.get('name'))
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
		obj = model_name.objects.get(slug=request.GET.get('name'))
		obj.active = 0
		obj.save()
	return HttpResponseRedirect(url)