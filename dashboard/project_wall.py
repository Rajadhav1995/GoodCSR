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
from taskmanagement.templatetags import common_tags
from taskmanagement.templatetags.common_tags import get_modified_by_user
from menu_decorators import check_loggedin_access

@check_loggedin_access
def get_project_updates(request):
#	start_date = '2017-01-01'
#	end_date = '2018-02-28'
	key = 'updates_wall'
	main_data = []
	utc=pytz.UTC
	today = datetime.now() + timedelta(days=1)
	slug = request.GET.get('slug')
	projectobj = Project.objects.get_or_none(slug=slug)
	start_date = projectobj.start_date
	task_list = Task.objects.filter(activity__project=projectobj,active=2).order_by('-id')
	plain_task = []
	history_task_data = []
	utc=pytz.UTC
	for t in task_list:
		data = {'task_name':t.name,'activity_name':t.activity.name,
				'supercategory':t.activity.super_category,'date':t.created,
				'created_by':t.created_by,'update_type':'tasks',
				'task_link':PMU_URL+'/managing/my-tasks/details/?slug='+slug+'&key=projecttasks&status=1'}
		plain_task.append(data)
		# added by priya where written a common function to get the task updates history
		history_data = common_tags.task_updates_list(key,t,start_date,today)
		for i in history_data:
		    history_task_data.append(i)
	main_data = history_task_data + plain_task
	budget_data = []
	budget_conf_list = list(ProjectBudgetPeriodConf.objects.filter(project=projectobj,active=2).values_list('id',flat=True))
	budget_period = BudgetPeriodUnit.objects.filter(budget_period__id__in=budget_conf_list,active=2).exclude(planned_unit_cost="")
	line_item_amount_list = list(budget_period.values_list('planned_unit_cost',flat=True))
	line_total = sum(map(float,line_item_amount_list))
	budget_data_list = []
	for q in budget_period:
		budgethistory = q.history.all()
		temp_var = 0
		for k in budgethistory:
			new_var = int(k.modified.strftime("%Y%m%d%H%M"))
			if int(new_var) != int(temp_var):
				data = 	{'date':k.modified.strftime("%Y-%m-%d-%H-%M"),'amount':k.planned_unit_cost,'modified_by':get_modified_by_user(k.modified_by)}
				budget_data_list.append(data)
			temp_var = new_var
	result = defaultdict(float)
	
	for d in budget_data_list:
		result[d['date']] += float(d['amount'])
	budget_final_dict = [{'date': name, 'amount': int(value)} for name, value in result.items()]
	budgetlist = []
	utc=pytz.UTC
	from pytz import timezone
	for c,d in zip(budget_final_dict,budget_data_list):
		
		history_date = datetime.strptime(c.get('date'), '%Y-%m-%d-%H-%M')
		history_date = history_date.replace(tzinfo=timezone('UTC')).replace(second=1)
		data = {'date':history_date,'amount':c.get('amount'),'update_type':'budget_history','modified_by':d.get('modified_by') if d.get('modified_by') else budget_period[0].created_by.attrs }
		budgetlist.append(data)
	file_data = []
	file_update = Attachment.objects.filter(active=2,created__range=[start_date,today],object_id=projectobj.id,content_type = ContentType.objects.get_for_model(projectobj))
	for f in file_update:
		history = f.history.all().order_by('modified')
		history_data = []
		for k in history[:2]:
			history_data.append({'name':k.name,'description':k.description,'file_name':k.attachment_file.split('/')[-1],'date':k.created,'update_type':'file','modified_by':get_modified_by_user(k.modified_by)})
		# import ipdb; ipdb.set_trace()
		file_data.append({'name':f.name,'created_by':f.created_by,'file_type':f.get_attachment_type_display(),'date':f.created,'update_type':'file','history':history_data,'image_type':f.timeline_progress,'image_url':PMU_URL + str(f.attachment_file.url) if f.attachment_file else '','file_name':f.attachment_file.url.split('/')[-1] if f.attachment_file else '','description':f.description})
	budgetlist.sort(key=lambda item:item['date'], reverse=True)
	final_data = main_data + file_data + budgetlist
	final_data.sort(key=lambda item:item['date'], reverse=True)
	key = 'updates'
	return render(request,'project-wall/project_updates.html',locals())


# @csrf_exempt	
def create_note(request):
	pass
