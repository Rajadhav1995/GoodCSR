import requests,ast
import math
import datetime
from django.contrib.contenttypes.models import ContentType
from datetime import timedelta,datetime
from django.shortcuts import render
from dateutil import relativedelta
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from media.models import Article,Section,ContactPersonInformation
from media.forms import ContactPersonForm,Attachment
from django.template import loader
from projectmanagement.models import Project,UserProfile,ProjectFunderRelation,ProjectParameter
from budgetmanagement.models import *
from budgetmanagement.manage_budget import get_budget_logic
from django.shortcuts import redirect

def report_form(request):
    #to save the report type and duration
    slug =  request.GET.get('slug')
    project = Project.objects.get_or_none(slug = request.GET.get('slug'))
    report_obj = ProjectReport.objects.get_or_none(project=project)
    user_id = request.session.get('user_id')
    import ipdb; ipdb.set_trace()
    user = UserProfile.objects.get_or_none(user_reference_id = user_id)
    if request.method == 'POST':
        data = request.POST
        project_obj = Project.objects.get_or_none(slug = data.get('project_slug'))
        project_report = ProjectReport.objects.create(project = project_obj,created_by = user,\
            report_type = data.get('report_type'),name = project_obj.name)
        project_report.start_date = data.get('start_date')
        project_report.end_date = data.get('end_date')
        project_report.save()
        return HttpResponseRedirect('report/detail/?report_id='+str(project_report.id)+'&project_slug='+data.get('project_slug'))
    return render(request,'report/report-form.html',locals())

def report_section(request):
    slug =  request.GET.get('slug')
    project = Project.objects.get_or_none(slug = request.GET.get('slug'))
    report_obj = ProjectReport.objects.get_or_none(project=project)
    # import ipdb; ipdb.set_trace()
    if report_obj:
        print "goodcsr"
        # return redirect('/some/url/')
        return redirect('/report/detail/?slug=rabri-devi')
    return render(request,'report/report-form.html',locals())

def report_detail(request):
    report_id = request.GET.get('report_id')
    project_slug = request.GET.get('project_slug')
    user_id = request.session.get('user_id')
    user = UserProfile.objects.get_or_none(user_reference_id = user_id)
    project = Project.objects.get_or_none(slug = project_slug)
    report_obj = ProjectReport.objects.get_or_none(project=project)
    funder_user = UserProfile.objects.filter(active=2,organization_type=1)
    partner = UserProfile.objects.filter(active=2,organization_type=2)
    mapping_view = ProjectFunderRelation.objects.get_or_none(project=project)
    if request.method == 'POST':
        data = request.POST
        project_obj = Project.objects.get_or_none(slug = data.get('project_slug'))
        project_report = ProjectReport.objects.get_or_none(id = data.get('report_id'))
        project_report.description = data.get('description')
        project_report.objective = data.get('objective')
        project_report.save()
        funder = request.POST.get('funder')
        total_budget = request.POST.get('total_budget')
        duration = request.POST.get('duration')
        beneficiaries_no = request.POST.get('beneficiaries_no')
        implementation_partner = request.POST.get('implementation_partner')
        if data.get('quarter_updates'):
            return HttpResponseRedirect('/report/quarter/update/?slug='+data.get('project_slug'))
        else:
            return HttpResponseRedirect('/project/summary/?slug='+data.get('project_slug')+'&key='+'summary')
    return render(request,'report/generation-form.html',locals())

def report_create(request):
    project_slug = request.GET.get('project_slug')
    project = Project.objects.get_or_none(slug = project_slug)
    report_obj = ProjectReport.objects.latest_one(project=project)
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
        if current_date > sd and current_date < ed:
            currentquarter_list.update({i:str(sd.date())+" to "+str(ed.date())})
        elif sd > current_date and ed >current_date:
            futurequarter_list.update({i:str(sd.date())+" to "+str(ed.date())})
        elif sd < current_date and ed < current_date:
            previousquarter_list.update({i:str(sd.date())+" to "+str(ed.date())})
        sd = ed + timedelta(days=1)
    return previousquarter_list,currentquarter_list,futurequarter_list

def get_quarter_report(request,itemlist,quarter):
    result = {}
    for line in itemlist:
        if str(quarter) == line.split('_')[2]:
            line_list = line.split('_')
            name = line.split('_')[0]
            result.update({name:request.POST.get(line)})
    return result

def get_report_based_quarter(request,projectreportobj,quarter_type,quarter_list,itemlist):
    for quarter,value in quarter_list.items():
        budget_period = value
        start_date = budget_period.split('to')[0].rstrip()
        end_date = budget_period.split('to')[1].lstrip()
        result = get_quarter_report(request,itemlist,quarter)
        quarter_report_dict = {
                        'project':projectreportobj,
                        'quarter_type':quarter_type,
                        'description':result.get("about-quarter",""),
                        'budget_utilization':result.get('budget-tranches',""),
                        'about_budget':result.get("about-budget",""),
                        'risks_mitigation':result.get("risk-mitigation",""),
                        'start_date':start_date,
                        'end_date':end_date,
                        'duration':result['duration'],
                        'quarter_order':quarter,
        }
        quarterreportobj = QuarterReportSection.objects.create(**quarter_report_dict)
    return quarterreportobj,result

def milestone_activity_save(request,name,description,result,quarterreportobj):
#    Common function to save the milestone and activities
    milestoneobj = ReportMilestoneActivity.objects.create(quarter=quarterreportobj,name=name,description=description)
    if result['paramter-selection']:
        reportparamterobj = ReportParameter.objects.create(quarter = quarterreportobj,keyparameter=ProjectParameter.objects.get(id=int(result['paramter-selection'])),description = result['about-parameter'])
    return milestoneobj

def image_save(request,milestoneobj,projectobj,result):
#    Common functionality to save the images
    user_obj = UserProfile.objects.get_or_none(user_reference_id = request.session.get('user_id'))
    image_dict = {
            'created_by' : user_obj,
            'attachment_file':result['img'],
            'description' : result['pic-description'], 
            'name' : projectobj.name,
            'attachment_type' : 1,
            'content_type' : ContentType.objects.get_for_model(milestoneobj),
            'object_id' : milestoneobj.id
    }
    imageobj = Attachment.objects.create(**image_dict)
    return imageobj

def genearte_report(request):
    slug = request.GET.get('slug')
    projectobj = ProjectReport.objects.filter(project__slug=slug)[0]
    previousquarter_list,currentquarter_list,futurequarter_list = {},{},{}
    project_paramterlist = ProjectParameter.objects.filter(project__slug=slug,parent=None)
    
    if projectobj:
        previousquarter_list,currentquarter_list,futurequarter_list = get_quarters(projectobj)
    if request.method == "POST":
        slug = request.POST.get('slug')
        projectreportobj = ProjectReport.objects.filter(project__slug=slug)[0]
        previousquarter_list,currentquarter_list,futurequarter_list = get_quarters(projectobj)
#    to save the previous quarter updates:
        quarter_type = 1
        quarter_list = previousquarter_list
        previous_itemlist = [str(k) for k,v in request.POST.items() if '_1_' in str(k) if k.split('_')[1]=='1']
        if previous_itemlist:
            quarterreportobj,result = get_report_based_quarter(request,projectreportobj,quarter_type,quarter_list,previous_itemlist)
            if result['milestone-name']:
                name = result['milestone-name']
                description = result['milestone-description']
                milestoneobj = milestone_activity_save(request,name,description,result,quarterreportobj)
                imageobj = image_save(request,milestoneobj,projectobj,result)

#    to save the Current quarter updates:
        current_itemlist = [str(k) for k,v in request.POST.items() if '_2_' in str(k) if k.split('_')[1]=='2']
        quarter_list = currentquarter_list
        quarter_type = 2
        if current_itemlist:
            quarterreportobj,result = get_report_based_quarter(request,projectreportobj,quarter_type,quarter_list,current_itemlist)
            if result['activity-name']:
                name = result['activity-name']
                description = result['activity-description']
                milestoneobj = milestone_activity_save(request,name,description,result,quarterreportobj)
                imageobj = image_save(request,milestoneobj,projectobj,result)
#    to save the Future quarter updates:
        future_itemlist = [str(k) for k,v in request.POST.items() if '_3_' in str(k) if k.split('_')[1]=='3']
        quarter_list = futurequarter_list
        quarter_type = 3
        if future_itemlist:
            quarterreportobj,result = get_report_based_quarter(request,projectreportobj,quarter_type,quarter_list,future_itemlist)
        return HttpResponseRedirect('/project/summary/?slug='+str(slug)+'&key=summary')
    return render(request,'report/quarter-update.html',locals())
    
    
