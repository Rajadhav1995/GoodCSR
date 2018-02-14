import requests,ast
from django.shortcuts import render
from taskmanagement.models import Task
from budgetmanagement.models import Budget
from projectmanagement.models import Project
from media.models import Attachment


def get_project_updates(request):
	projobj = Project.objects.get_or_none(slug='test-project-feb5')
	task_updates = Task.objects.filter(active=2)
	budget_update = Budget.objects.filter(active=2)
	file_update = Attachment.objects.filter(active=2)
	return render(request,'project-wall/project_updates.html',locals())
