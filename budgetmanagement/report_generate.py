import requests,ast
import math
import datetime
from datetime import timedelta,datetime
from django.shortcuts import render
from dateutil import relativedelta
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from media.models import Article,Section,ContactPersonInformation
from media.forms import ContactPersonForm
from django.template import loader
from projectmanagement.models import Project,UserProfile,ProjectFunderRelation
from budgetmanagement.models import *
from budgetmanagement.manage_budget import get_budget_logic


def report_form(request):
    slug =  request.GET.get('slug')
    project = Project.objects.get_or_none(slug = request.GET.get('slug'))
    funder_user = UserProfile.objects.filter(active=2,organization_type=1)
    partner = UserProfile.objects.filter(active=2,organization_type=2)
    mapping_view = ProjectFunderRelation.objects.get_or_none(project=project)
    user_id = request.session.get('user_id')
    user = UserProfile.objects.get_or_none(user_reference_id = user_id)
    return render(request,'report/generation-form.html',locals())

def report_detail(request):
    user_id = request.session.get('user_id')
    user = UserProfile.objects.get_or_none(user_reference_id = user_id)
    slug =  request.GET.get('slug')
    project_obj = Project.objects.get_or_none(slug = slug)
    funder = ProjectFunderRelation.objects.get(project=project_obj)
    print funder.funder.name
    return render(request,'report/report-detail.html',locals())

def get_quarter_report_logic(projectobj):
    ''' common functionality to get the start date,end date and no of quarter'''
    sd = projectobj.start_date
    projectobj_enddate = projectobj.end_date
    if sd.day >= 15:
        year = sd.year+1 if sd.month == 12 else sd.year
        sd = sd.replace(day=01,month = sd.month+1,year=year)
    elif sd.day < 15:
        sd = sd.replace(day=01,month = sd.month,year=sd.year)
    ed = projectobj.end_date
    no_of_quarters = math.ceil(float(((ed.year - sd.year) * 12 + ed.month - sd.month))/3)
    output_data = {'sd':sd,'projectobj_enddate':projectobj_enddate,
                   'ed':ed,'no_of_quarters':no_of_quarters}
    return output_data

def get_quarters(projectobj):
    ''' To get the quarter list i this format 2017-10-01 to 2017-12-31 '''
    data = get_quarter_report_logic(projectobj)
    sd = data['sd']
    projectobj_enddate = data['projectobj_enddate']
    no_of_quarters = data['no_of_quarters']
    ed = data['ed']
    previousquarter_list = {}
    currentquarter_list = {}
    futurequarter_list = {}
    for i in range(int(no_of_quarters)):

        ed = sd+relativedelta.relativedelta(months=3)
        ed = ed - timedelta(days=1)
        sd = datetime.strptime(str(sd)[:19], '%Y-%m-%d %H:%M:%S')
        ed = datetime.strptime(str(ed)[:19], '%Y-%m-%d %H:%M:%S')
        projectobj_enddate = datetime.strptime(str(projectobj_enddate)[:19], '%Y-%m-%d %H:%M:%S')
        if ed > projectobj_enddate:
            ed = projectobj_enddate
        current_date = datetime.strptime(str(datetime.now())[:19], '%Y-%m-%d %H:%M:%S')
        print current_date, sd, ed
        if current_date > sd and current_date < ed:
            currentquarter_list.update({i:str(sd.date())+" to "+str(ed.date())})
        elif sd > current_date and ed >current_date:
            futurequarter_list.update({i:str(sd.date())+" to "+str(ed.date())})
        elif sd < current_date and ed < current_date:
            previousquarter_list.update({i:str(sd.date())+" to "+str(ed.date())})
        sd = ed + timedelta(days=1)
    return previousquarter_list,currentquarter_list,futurequarter_list

def genearte_report(request):
    slug = request.GET.get('slug')
    projectobj = ProjectReport.objects.get_or_none(project__slug=slug)
    previousquarter_list,currentquarter_list,futurequarter_list = {},{},{}
    if projectobj:
        previousquarter_list,currentquarter_list,futurequarter_list = get_quarters(projectobj)
    if request.method == "POST":
        print request.POST
    return render(request,'report/quarter-update.html',locals())
