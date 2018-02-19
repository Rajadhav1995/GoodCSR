import requests,ast
from django.shortcuts import render
from taskmanagement.models import Task
from budgetmanagement.models import Budget
from projectmanagement.models import Project
from django.contrib.contenttypes.models import ContentType
from media.models import Attachment
from pmu.settings import PMU_URL


def get_project_updates(request):
	start_date = '2018-01-01'
	end_date = '2018-02-28'
	main_data = []
	projectobj = Project.objects.get_or_none(slug='test-project-feb5')
	task_updates = Task.objects.filter(active=2)
	# task_history = task_updates.history.all()
	project_task = 
	
	budget_update = Budget.objects.filter(active=2,project=projectobj,created__range=[start_date,end_date])
	budget_data = []
	for b in budget_update:
		budget_data.append({'created_by':'','name':b.name,'date':b.created,'is_history':0,'update_type':'budget'})
	budget_history_object = Budget.objects.filter(active=2,project=projectobj)
	for i in budget_history_object:
		budget_history = i.history.all()
		budget_history_new = budget_history.filter(created__range=[start_date,end_date])
		for h in budget_history:
			budget_data.append({'name':h.name,'date':h.created,'is_history':1,'update_type':'budget'})
	
	file_data = []
	file_update = Attachment.objects.filter(active=2,created__range=[start_date,end_date],object_id=projectobj.id,content_type = ContentType.objects.get_for_model(projectobj))
	for f in file_update:
		
		history = f.history.all().order_by('created')
		history_data = []
		for k in history:
			history_data.append({'name':k.name,'description':k.description,'file_name':k.attachment_file.split('/')[-1],'date':k.created,'update_type':'file'})
		file_data.append({'name':f.name,'created_by':f.created_by,'file_type':f.get_attachment_type_display(),'date':f.created,'update_type':'file','history':history_data,'image_type':f.timeline_progress,'image_url':PMU_URL + str(f.attachment_file)})

	# file_history_object = Attachment.objects.filter(active=2,object_id=projectobj.id,content_type = ContentType.objects.get_for_model(projectobj))
	# for f in file_history_object:
	# 	file_history = f.history.filter(created__range=[start_date,end_date])
	# 	for j in file_history:
	# 		file_data.append({'name':j.name,'created_by':j.history_user,'file_type':j.get_attachment_type_display(),'date':j.created,'update_type':'file'})
	file_data.sort(key=lambda item:item['date'], reverse=True)
	# import ipdb; ipdb.set_trace()
	return render(request,'project-wall/project_updates.html',locals())
