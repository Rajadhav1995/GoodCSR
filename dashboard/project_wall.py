import requests,ast
from django.shortcuts import render
from taskmanagement.models import Task,Activity
from budgetmanagement.models import Budget
from projectmanagement.models import Project
from django.contrib.contenttypes.models import ContentType
from media.models import Attachment,Comment
from pmu.settings import PMU_URL
from datetime import datetime,timedelta
from itertools import chain

def get_project_updates(request):
	start_date = '2017-01-01'
	end_date = '2018-02-28'
	# import ipdb; ipdb.set_trace()
	main_data = []
	today = datetime.today().date()
	tomorrow = today + timedelta(days=1)
	remain_days = today + timedelta(days=2)
	slug = request.GET.get('slug')
	status = 1

	projectobj = Project.objects.get_or_none(slug=slug)
	user = projectobj.created_by
	activity_list = list(Activity.objects.filter(project=projectobj).values_list('id', flat=True))
	proj_task=Task.objects.filter(activity__id__in=list(activity_list))
	tasks_today = projectobj.get_todays_tasks(today,user,status)
	tasks_tomorrow = projectobj.get_todays_tasks(tomorrow,user,status)
	tasks_remain = projectobj.get_remaining_tasks(remain_days,user,status)
	closed_tasks = Task.objects.filter(status=2,activity__project__id=projectobj.id).order_by('-id')
	remain_tasks = list(set(list(chain(tasks_remain,closed_tasks))))
	task_listing = list(chain(tasks_today ,tasks_tomorrow,remain_tasks))
	plain_task = []
	history_task_data = []
	for t in task_listing:
		data = {'task_name':t.name,'activity_name':t.activity.name,
				'supercategory':t.activity.super_category,'date':t.created,
				'created_by':t.created_by,'update_type':'tasks'}
		plain_task.append(data)
		history_obj = t.history.filter(created__range=[start_date,end_date])[:10]
		for k in history_obj:
			time = k.modified
			start_time = time.replace(microsecond=0)
			end_time = time.replace(microsecond=999999)
			comment_obj = Comment.objects.get_or_none(created__range=[start_time,end_time])
			attach_obj = Attachment.objects.get_or_none(created=time)
			previous_task_progress = k.get_previous_by_created().task_progress
			history_data = {'task_name':k.name,'activity_name':k.activity.name,
			'supercategory':k.activity.super_category,'date':k.created,
			'task_progress':k.task_progress,'previous_task_progress':previous_task_progress,
			'activity_name':k.activity.name,'supercategory':k.activity.super_category,
			'update_type':'tasks_history'}
			if attach_obj:
				history_data.update({'file_name':attach_obj.name,'file_description':attach_obj.description,'file_url':attach_obj.attachment_file})
			if comment_obj:
				history_data.update({'comment_text':comment_obj.text})
			history_task_data.append(history_data)

	main_data = history_task_data + plain_task

	budget_data = []
	budget_conf_list = list(ProjectBudgetPeriodConf.objects.filter(project=projectobj).values_list('id',flat=True))
	budget_period = list(BudgetPeriodUnit.objects.filter(budget_period__id__in=budget_conf_list).values_list('planned_unit_cost',flat=True))






	# import ipdb; ipdb.set_trace()
	# task = Task.objects.filter(status=2,activity__project__id=projectobj.id).order_by('-id')
	task_data = []
	for i in task_listing:
		task_history = i.history.all()[:5]
		for t in task_history:
			task_time = t.modified
			task_prev_tick = task_time.second -1
			try:
				start_time = task_time.replace(microsecond=499999,second=task_prev_tick)
			except:
				start_time = task_time.replace(microsecond=499999,second=59)
			end_time = task_time.replace(microsecond=999999)
			attach_obj = Attachment.objects.get_or_none(created__range=(start_time,end_time))
			previous_task_progress = t.get_previous_by_created().task_progress
			# import ipdb; ipdb.set_trace()
			comment_ = Comment.objects.get_or_none(active=2,content_type=ContentType.objects.get(model=('task')),object_id=i.id,created__range=(start_time,end_time))
			task_history_data = {'task_name':t.name,'activity_name':t.activity.name,
			'supercategory':t.activity.super_category,'date':t.created,
			'task_progress':t.task_progress,'previous_task_progress':previous_task_progress,
			'activity_name':t.activity.name,'supercategory':i.activity.super_category,}
			print i.activity.super_category				
			if comment_:
				task_history_data.update({'comment_text':comment_.text})

		# tas = {'task_name':i.name,'activity_name':i.activity.name,
		# 		'supercategory':i.activity.super_category,'date':i.created,
		# 		'history':task_history_data}
			task_data.append(task_history_data)
	# task_history = task_updates.history.all()

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
	main_data.sort(key=lambda item:item['date'], reverse=True)

	# import ipdb; ipdb.set_trace()
	return render(request,'project-wall/project_updates_old.html',locals())
