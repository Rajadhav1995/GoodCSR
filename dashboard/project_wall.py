import requests,ast
from django.shortcuts import render_to_response
from django.shortcuts import render
from taskmanagement.models import Task,Activity
from budgetmanagement.models import Budget,ProjectBudgetPeriodConf,BudgetPeriodUnit,Tranche
from django.http import HttpResponse,HttpResponseRedirect
from projectmanagement.models import Project,UserProfile,ProjectParameter,ProjectParameterValue
from django.contrib.contenttypes.models import ContentType
from media.models import Attachment,Comment, Note
from pmu.settings import PMU_URL
from datetime import datetime,timedelta
from itertools import chain
from collections import defaultdict
from dateutil import parser
from django.core.cache import cache
import pytz
from django.contrib import messages
from taskmanagement.templatetags import common_tags
from taskmanagement.templatetags.common_tags import get_modified_by_user,string_trim,read_more_text
from menu_decorators import check_loggedin_access
from media.forms import NoteForm

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
		
		result[d['date']] += float(d['amount']) if d['amount'] else float(0)

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
		file_data.append({'name':f.name,'created_by':f.created_by,'file_type':f.get_attachment_type_display(),'date':f.created,'update_type':'file','history':history_data,'image_type':f.timeline_progress,'image_url':PMU_URL + str(f.attachment_file.url) if f.attachment_file else '','file_name':string_trim(f.attachment_file.url.split('/')[-1]) if f.attachment_file else '','description':f.description})
	parameter_data = []
	parameter_value = ProjectParameterValue.objects.filter(keyparameter__project=projectobj,keyparameter__parent=None)
	parameter_created_data = []
	for p in parameter_value:
		data = {'date':p.created,'upload_date':p.start_date,
				'modified_by':get_modified_by_user(p.modified_by),
				'update_type':'parameter','keyparameter_name':p.keyparameter.name}
		parameter_data.append(data)
	parameter_history_data = []
	project_parameter = ProjectParameter.objects.filter(project=projectobj,parent__isnull=True)
	
	for parameter in project_parameter:
		
		created_data = {'modified_by':get_modified_by_user(parameter.modified_by),'parameter_name':parameter.name,
						'date':parameter.created,'update_type':'parameter_created'}
		parameter_created_data.append(created_data)
		parameter_time = int(parameter.created.strftime("%Y%m%d%H%M%S"))
		parameter_history = parameter.history.all()[0::2]

		for history in parameter_history:
			history_time = int(history.modified.strftime("%Y%m%d%H%M%S"))
			if int(history_time) != int(parameter_time):
				data = {'date':history.modified,'id':parameter.id,
					'modified_by':get_modified_by_user(history.modified_by),
					'parameter_name':history.name,'update_type':'parameter_history'}
				parameter_history_data.append(data)
	note_list = get_project_note(projectobj,request)
	tranche_list = get_trance_updates(projectobj,slug)
	budgetlist.sort(key=lambda item:item['date'], reverse=True)
	final_data = main_data + file_data + budgetlist + note_list + parameter_data + parameter_history_data + parameter_created_data + tranche_list
	final_data.sort(key=lambda item:item['date'], reverse=True)
	key = 'updates'
	return render(request,'project-wall/project_updates.html',locals())

def get_project_note(projectobj,request):
	note_obj = Note.objects.filter(project=projectobj)
	note_list = []
	for n in note_obj:
		short_comment_text,more_comment_text = read_more_text(n.comment)
		short_description_text,more_description_text = read_more_text(n.description)
		data = {'short_comment':short_comment_text,'short_description':short_description_text,'date':n.created,
				'attachment_name':string_trim(n.attachment_file.url.split('/')[-1]) if n.attachment_file else '',
				'attachment_link':PMU_URL + str(n.attachment_file.url) if n.attachment_file else '',
				'update_type':'note','created_by':n.created_by,
				'description':n.description,'more_comment':more_comment_text}
		note_list.append(data)
	return note_list

def get_trance_updates(projectobj,slug):
	tranches = Tranche.objects.filter(project=projectobj)
	tranche_list = []
	for t in tranches:
		data = {'date':t.created,'update_type':'tranche','planned_amount':t.planned_amount,
				'modified_by':get_modified_by_user(t.modified_by),'tranche_name':t.name,
				'tranche_url':PMU_URL + '/project/tranche/list/' + '?slug='+slug}
		tranche_list.append(data)
		
		tranche_history_data = []
		for th in t.history.all()[0::2]:
			history_data = {'date':th.created,'update_type':'tranche_history','planned_amount':th.planned_amount,
				'modified_by':get_modified_by_user(th.modified_by),'tranche_name':th.name,
				'tranche_url':PMU_URL + '/project/tranche/list/' + '?slug='+slug}
			tranche_history_data.append(history_data)
	tranche_list_final = tranche_history_data + tranche_list
	tranche_list_final.sort(key=lambda item:item['date'], reverse=True)
	return tranche_list_final

def create_note(request):
	created_by = UserProfile.objects.get_or_none(id=request.session.get('user_id'))
	slug=request.GET.get('slug')
	if request.method=='POST':
		project_slug = request.POST.get('slug')
		projectobj = Project.objects.get(slug=project_slug)
		note_create = Note.objects.create(project=projectobj,\
						comment=request.POST.get('comment'),
						description=request.POST.get('description'),
						attachment_file=request.FILES['attachment'],
						created_by=created_by)
		messages.success(request, 'Note added successfully!')
		# return HttpResponseRedirect('/dashboard/updates/?slug='+str(project_slug))
		return HttpResponseRedirect('/dashboard/add/note/?slug='+str(project_slug))
	return render(request,'project-wall/create-note.html',locals())
