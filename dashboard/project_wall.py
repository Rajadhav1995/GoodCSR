import requests,ast
from django.shortcuts import render
from taskmanagement.models import Task,Activity
from budgetmanagement.models import Budget,ProjectBudgetPeriodConf,BudgetPeriodUnit
from projectmanagement.models import Project,UserProfile
from django.contrib.contenttypes.models import ContentType
from media.models import Attachment,Comment
from pmu.settings import PMU_URL
from datetime import datetime,timedelta
from itertools import chain
from collections import defaultdict
from dateutil import parser
import pytz


def get_modified_by_user(user_id):
	user_object = UserProfile.objects.get_or_none(user_reference_id=oo)
	if user_object:
		return user_object.attrs

def get_project_updates(request):
	start_date = '2017-01-01'
	end_date = '2018-02-28'
	main_data = []
	today = datetime.today().date()
	slug = request.GET.get('slug')
	projectobj = Project.objects.get_or_none(slug=slug)
	task_list = Task.objects.filter(activity__project=projectobj,active=2).order_by('-id')
	plain_task = []
	history_task_data = []
	for t in task_list:
		data = {'task_name':t.name,'activity_name':t.activity.name,
				'supercategory':t.activity.super_category,'date':t.created,
				'created_by':t.created_by,'update_type':'tasks',
				'task_link':PMU_URL+'/managing/my-tasks/details/?slug='+slug+'&key=projecttasks&status=1'}
		plain_task.append(data)
		history_obj = t.history.filter(created__range=[start_date,end_date]).order_by('-id')
		temp_var = 0
		for k in history_obj:
			time_check = int(k.modified.strftime("%Y%m%d%H%M%S"))
			if (int(time_check)-int(temp_var)) < 10:
				pass
			else:
				time = k.modified
				start_time = time.replace(microsecond=0)
				end_time = time.replace(microsecond=999999)
				comment_obj = Comment.objects.get_or_none(created__range=[start_time,end_time])
				attach_obj = Attachment.objects.get_or_none(created=time)
				previous_task_progress = k.get_previous_by_created().task_progress

				# created_by = UserProfile.objects.get(user__id=k.modified_by)
				if previous_task_progress != k.task_progress:
					history_data = {'task_name':k.name,'activity_name':k.activity.name,
					'supercategory':k.activity.super_category,'date':k.modified,
					'task_progress':k.task_progress,'previous_task_progress':previous_task_progress,
					'activity_name':k.activity.name,'supercategory':k.activity.super_category,
					'update_type':'tasks_history','created_by':'',
					'task_link':PMU_URL+'/managing/my-tasks/details/?slug='+slug+'&key=projecttasks&status=1'}
					print k.modified, "task_date"
					if attach_obj:
						history_data.update({'file_name':attach_obj.name,'file_description':attach_obj.description,'file_url':PMU_URL + '/' +str(attach_obj.attachment_file)})
					if comment_obj:
						history_data.update({'comment_text':comment_obj.text})
					history_task_data.append(history_data)
				temp_var = time_check
	main_data = history_task_data + plain_task

	budget_data = []
	
	budget_conf_list = list(ProjectBudgetPeriodConf.objects.filter(project=projectobj,active=2).values_list('id',flat=True))
	budget_period = BudgetPeriodUnit.objects.filter(budget_period__id__in=budget_conf_list,active=2).exclude(planned_unit_cost="")
	line_item_amount_list = list(budget_period.values_list('planned_unit_cost',flat=True))


	line_total = sum(map(float,line_item_amount_list))

	budget_data_list = []
	for q in budget_period:
		budgethistory = q.history.all()
		for k in budgethistory:
			data = 	{'date':k.modified.strftime("%Y-%m-%d-%H-%M"),'amount':k.planned_unit_cost}
			budget_data_list.append(data)
	result = defaultdict(float)
	for d in budget_data_list:
		result[d['date']] += float(d['amount'])
	budget_final_dict = [{'date': name, 'amount': value} for name, value in result.items()]
	budgetlist = []
	utc=pytz.UTC
	from pytz import timezone
	for c in budget_final_dict[:10]:
		history_date = datetime.strptime(c.get('date'), '%Y-%m-%d-%H-%M')
		history_date = history_date.replace(tzinfo=timezone('UTC')).replace(second=1)
		data = {'date':history_date,'amount':c.get('amount'),'update_type':'budget_history'}
		budgetlist.append(data)
	file_data = []
	file_update = Attachment.objects.filter(active=2,created__range=[start_date,end_date],object_id=projectobj.id,content_type = ContentType.objects.get_for_model(projectobj))
	for f in file_update:
		history = f.history.all().order_by('modified')
		history_data = []
		for k in history:
			history_data.append({'name':k.name,'description':k.description,'file_name':k.attachment_file.split('/')[-1],'date':k.created,'update_type':'file'})
		file_data.append({'name':f.name,'created_by':f.created_by,'file_type':f.get_attachment_type_display(),'date':f.created,'update_type':'file','history':history_data,'image_type':f.timeline_progress,'image_url':PMU_URL +'/' + str(f.attachment_file)})

	budgetlist.sort(key=lambda item:item['date'], reverse=True)
	final_data = main_data + file_data + budgetlist
	final_data.sort(key=lambda item:item['date'], reverse=True)
	key = 'updates'
	return render(request,'project-wall/project_updates.html',locals())


# @csrf_exempt	
def create_note(request):
	return
