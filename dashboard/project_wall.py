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

# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
def get_date_range(request,projectobj):
	
	if request.POST.get('from'):
		start_date = datetime.strptime(request.POST.get('from'),"%m/%d/%Y")
	else:
		start_date = projectobj.start_date
	if request.POST.get('to'):
		end_date = datetime.strptime(request.POST.get('to'),"%m/%d/%Y")
	else:
		end_date = datetime.now() + timedelta(days=1)
	# import ipdb; ipdb.set_trace()
	return start_date,end_date


@check_loggedin_access
def get_project_updates(request):
#	start_date = '2017-01-01'
#	end_date = '2018-02-28'	
	
	key = 'updates_wall'
	main_data = []
	utc=pytz.UTC
		
	filter_key = request.GET.get('filter')
	slug = request.GET.get('slug')
	projectobj = Project.objects.get_or_none(slug=slug)
	start_date,end_date = get_date_range(request,projectobj)
	
	task_list = Task.objects.filter(activity__project=projectobj,active=2,created__range=[start_date,end_date]).order_by('-id')
	
	plain_task = []
	history_task_data = []
	if request.GET.get('filter') == 'task' or request.GET.get('filter') == None:
		for t in task_list:
			data = {'task_name':t.name,'activity_name':t.activity.name,
					'supercategory':t.activity.super_category,'date':t.created,
					'created_by':t.created_by,'update_type':'tasks',
					'task_link':PMU_URL+'/managing/my-tasks/details/?slug='+slug+'&key=projecttasks&status=1'}
			plain_task.append(data)
			# added by priya where written a common function to get the task updates history
			history_data = common_tags.task_updates_list(key,t,start_date,end_date)
			for i in history_data:
			    history_task_data.append(i)
	main_data = history_task_data + plain_task
	budget_final_list = []
	if request.GET.get('filter') == 'budget' or request.GET.get('filter') == None:
		budget_final_list = get_budget_updates(projectobj,start_date,end_date)
	file_data_final = []
	timeline_data_final = []
	if request.GET.get('filter') == 'file' or request.GET.get('filter') == 'timeline' or request.GET.get('filter') == None:
		file_data_final = get_file_updates(projectobj,start_date,end_date,filter_key)
	final_parameter_data = []
	if request.GET.get('filter') == 'parameter' or request.GET.get('filter') == None:
		final_parameter_data = get_parameter_updates(projectobj,start_date,end_date)
	note_list = []
	if request.GET.get('filter') == 'note' or request.GET.get('filter') == None:
		note_list = get_project_note(projectobj,request,start_date,end_date)
	tranche_list = []
	if request.GET.get('filter') == 'tranche' or request.GET.get('filter') == None:
		tranche_list = get_tranche_update(projectobj,slug,start_date,end_date)
	budget_final_list.sort(key=lambda item:item['date'], reverse=True)
	filter_dict = {'task':main_data,'note':note_list}
	final_data = main_data + file_data_final + budget_final_list + note_list + final_parameter_data + tranche_list
	if filter_key == 'task':
		final_data = main_data
	final_data.sort(key=lambda item:item['date'], reverse=True)
	key = 'updates'
	url = PMU_URL
	return render(request,'project-wall/project_updates.html',locals())

def get_file_updates(projectobj,start_date,end_date,filter_key):
	file_data = []
	timeline_data = []
	file_update = Attachment.objects.filter(active=2,created__range=[start_date,end_date],object_id=projectobj.id,content_type = ContentType.objects.get_for_model(projectobj))
	for f in file_update:

		history = f.history.filter(modified__range=[start_date,end_date]).order_by('modified')
		history_data = []

		for k in history[:2]:
			history_data.append({'name':k.name,'description':k.description,'file_name':k.attachment_file.split('/')[-1],'date':k.created,'update_type':'file','modified_by':get_modified_by_user(k.modified_by)})
		if f.timeline_progress == True and f.attachment_type == 1:
			timeline_data.append({'name':f.name,'created_by':f.created_by,'file_type':f.get_attachment_type_display(),'date':f.created,'update_type':'file','history':history_data,'image_type':f.timeline_progress,'image_url':PMU_URL + str(f.attachment_file.url) if f.attachment_file else '','file_name':string_trim(f.attachment_file.url.split('/')[-1]) if f.attachment_file else '','description':f.description})
		else:
			file_data.append({'name':f.name,'created_by':f.created_by,'file_type':f.get_attachment_type_display(),'date':f.created,'update_type':'file','history':history_data,'image_type':f.timeline_progress,'image_url':PMU_URL + str(f.attachment_file.url) if f.attachment_file else '','file_name':string_trim(f.attachment_file.url.split('/')[-1]) if f.attachment_file else '','description':f.description})
	if filter_key == 'timeline':
		final_file_data = timeline_data
	elif filter_key == 'file':
		final_file_data = file_data
	else:
		final_file_data = timeline_data + file_data
	return final_file_data

def get_parameter_updates(projectobj,start_date,end_date):
	parameter_data = []
	parameter_value = ProjectParameterValue.objects.filter(keyparameter__project=projectobj,keyparameter__parent=None,created__range=[start_date,end_date])
	parameter_created_data = []
	for p in parameter_value:
		data = {'date':p.created,'upload_date':p.start_date,
				'modified_by':get_modified_by_user(p.modified_by) if p.modified_by else projectobj.created_by.attrs,
				'update_type':'parameter','keyparameter_name':p.keyparameter.name}
		parameter_data.append(data)
	parameter_history_data = []
	project_parameter = ProjectParameter.objects.filter(project=projectobj,parent__isnull=True,created__range=[start_date,end_date])
	
	for parameter in project_parameter:
		
		created_data = {'modified_by':get_modified_by_user(parameter.modified_by) if parameter.modified_by else projectobj.created_by.attrs ,'parameter_name':parameter.name,
						'date':parameter.created,'update_type':'parameter_created'}
		parameter_created_data.append(created_data)
		parameter_time = int(parameter.created.strftime("%Y%m%d%H%M%S"))
		parameter_history = parameter.history.filter(modified__range=[start_date,end_date])[0::2]
		for history in parameter_history:
			history_time = int(history.modified.strftime("%Y%m%d%H%M%S"))
			if int(history_time) != int(parameter_time):
				data = {'date':history.modified,'id':parameter.id,
					'modified_by':get_modified_by_user(history.modified_by) if history.modified_by else projectobj.created_by.attrs,
					'parameter_name':history.name,'update_type':'parameter_history'}
				parameter_history_data.append(data)
	final_parameter_data = parameter_history_data + parameter_data + parameter_created_data
	return final_parameter_data

def get_project_note(projectobj,request,start_date,end_date):
	note_obj = Note.objects.filter(project=projectobj,created__range=[start_date,end_date])
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
	tranche_history_data = []
	for t in tranches:
		temp_var = 0
		for th in t.history.all():
			new_var = int(th.modified.strftime("%Y%m%d%H%M"))
			modified_time = int(th.modified.strftime("%Y%m%d%H%M%S"))
			created_time = int(th.created.strftime("%Y%m%d%H%M%S"))
			if (int(new_var) != int(temp_var)):
				if created_time != modified_time:
					history_data = {'date':th.modified,'update_type':'tranche_history','planned_amount':th.planned_amount,
					'modified_by':get_modified_by_user(th.modified_by),'tranche_name':th.name,
					'tranche_url':PMU_URL + '/project/tranche/list/' + '?slug='+slug}
				else:
					history_data = {'date':th.modified,'update_type':'tranche','planned_amount':th.planned_amount,
					'modified_by':get_modified_by_user(th.modified_by),'tranche_name':th.name,
					'tranche_url':PMU_URL + '/project/tranche/list/' + '?slug='+slug}

				tranche_history_data.append(history_data)
			temp_var = new_var
	tranche_history_data.sort(key=lambda item:item['date'], reverse=True)
	return tranche_history_data

def get_tranche_update(projectobj,slug,start_date,end_date):
	
	tranches = Tranche.objects.filter(active=2,project=projectobj,created__range=[start_date,end_date]).order_by('id')
	tranche_list = []
	tranche_history_data = []
	for t in tranches:
		data = {'date':t.created,'update_type':'tranche','planned_amount':t.planned_amount,
				'modified_by':get_modified_by_user(t.modified_by) if t.modified_by else projectobj.created_by.attrs,'tranche_name':t.name,
				'tranche_url':PMU_URL + '/project/tranche/list/' + '?slug='+slug}
		tranche_list.append(data)
		temp_var = 0
		for th in t.history.filter(modified__range=[start_date,end_date]):

			new_var = int(th.modified.strftime("%Y%m%d%H%M%S"))
			modified_time = int(th.modified.strftime("%Y%m%d%H%M%S"))
			created_time = int(th.created.strftime("%Y%m%d%H%M%S"))
			if (temp_var != new_var) and (created_time != modified_time) and ((th.utilized_amount == th.get_previous_by_history_date().utilized_amount)):# or (th.planned_amount != th.get_previous_by_history_date().planned_amount)):
				
				history_data = {'date':th.modified,'update_type':'tranche_history','planned_amount':th.planned_amount,
					'modified_by':get_modified_by_user(t.modified_by) if t.modified_by else projectobj.created_by.attrs,
					'tranche_name':th.name,
					'tranche_url':PMU_URL + '/project/tranche/list/' + '?slug='+slug}
				tranche_history_data.append(history_data)
			temp_var = new_var
	final_tranche = tranche_list + tranche_history_data
	final_tranche.sort(key=lambda item:item['date'], reverse=True)
	return final_tranche

def get_budget_updates(projectobj,start_date,end_date):
	budgetlist = []
	budget_conf_list = list(ProjectBudgetPeriodConf.objects.filter(project=projectobj,active=2).values_list('id',flat=True))
	budget_period = BudgetPeriodUnit.objects.filter(budget_period__id__in=budget_conf_list,active=2,created__range=[start_date,end_date]).exclude(planned_unit_cost="")
	line_item_amount_list = list(budget_period.values_list('planned_unit_cost',flat=True))

	line_total = sum(map(float,line_item_amount_list))

	budget_data_list = []
	budget_count = budget_period.count()
	for q in budget_period:
		budgethistory = q.history.filter(modified__range=[start_date,end_date])
		temp_var = 0
		for k in budgethistory:
			new_var = int(k.modified.strftime("%Y%m%d%H%M"))
			
			if int(new_var) != int(temp_var):
				data = 	{'date':k.modified.strftime("%Y-%m-%d-%H-%M"),'amount':k.planned_unit_cost,'modified_by':get_modified_by_user(k.modified_by),'utilized_amount':k.utilized_unit_cost}

				budget_data_list.append(data)
			temp_var = new_var
	result = defaultdict(float)
	items = defaultdict(list)
	for idx,d in enumerate(budget_data_list):
		result[d['date']] += float(d['amount']) if d['amount'] else float(0)
		items[d['date']].append(d['amount'])
	budget_final_dict = [{'date': name, 'amount': int(value)} for name, value in result.items()]
	count_budget_list = [{'date': name, 'count': len(value)} for name, value in items.items()]
	
	utc=pytz.UTC
	from pytz import timezone
	for c,d,e in zip(budget_final_dict,budget_data_list,count_budget_list):
		
		history_date = datetime.strptime(c.get('date'), '%Y-%m-%d-%H-%M')
		history_date = history_date.replace(tzinfo=timezone('UTC')).replace(second=1)
		if e.get('count') == budget_count or e.get('count') == budget_count-1:
			data = {'date':history_date,'amount':c.get('amount'),'update_type':'budget_history','modified_by':d.get('modified_by') if d.get('modified_by') else budget_period[0].created_by.attrs }
			budgetlist.append(data)
	return budgetlist

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