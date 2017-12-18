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
from media.models import (Article,Section,ContactPersonInformation,
            ProjectLocation,Attachment)
from media.forms import ContactPersonForm,Attachment
from django.template import loader
from projectmanagement.models import Project,UserProfile,ProjectFunderRelation,ProjectParameter
from taskmanagement.models import Milestone,Activity,Task
from budgetmanagement.models import *
from budgetmanagement.manage_budget import get_budget_logic
from django.shortcuts import redirect
from pmu.settings import PMU_URL

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template.loader import render_to_string



def report_form(request):
    #to save the report type and duration
    slug =  request.GET.get('slug')
    project = Project.objects.get_or_none(slug = request.GET.get('slug'))
    if not project:
        project = Project.objects.get_or_none(slug = request.POST.get('project_slug'))
    user_id = request.session.get('user_id')
    user = UserProfile.objects.get_or_none(user_reference_id = user_id)
    budget_obj = Budget.objects.get_or_none(project=project)
    if budget_obj:
        from budgetmanagement.manage_budget import get_budget_quarters
        budget_quarters = get_budget_quarters(budget_obj) 
        if request.method == 'POST':
            data = request.POST
            report_id=data.get('report_id')
            project_obj = Project.objects.get_or_none(slug = data.get('project_slug'))
            quarter_ids = data.get('quarter_type')
            dates = budget_quarters[int(quarter_ids)]
            dates_list = dates.split(' to ')
            budget_end_date = dates_list[1] if dates_list else '' 
            budget_start_date = dates_list[0] if dates_list else '' 
            project_report ,created = ProjectReport.objects.get_or_create(project = project_obj,created_by = user,\
                report_type = data.get('report_type'),start_date  = budget_start_date,
                name = project_obj.name,end_date = budget_end_date)
            if created or int(project_report.active) == 0 :
                project_report.active = 2
                project_report.save()
                return HttpResponseRedirect('/report/final/design/?slug='+data.get('project_slug')+'&report_id='+str(project_report.id))
            else:
                quarter_msg = "Already Report is generated to this Quarter"
    else :
        msg = "Budget is not created"
    return render(request,'report/report-form.html',locals())

def report_listing(request):
# listing of the generated reports in the lisiting page
    slug =  request.GET.get('slug')
    project = Project.objects.get_or_none(slug = request.GET.get('slug'))
    report_obj = ProjectReport.objects.filter(project=project,active=2)
    budget_obj = Budget.objects.get_or_none(project=project)
    from budgetmanagement.manage_budget import get_budget_quarters
    budget_quarters = get_budget_quarters(budget_obj) 
    return render(request,'report/listing.html',locals())

def save_section_answers(quest_ids,project_report,request,data,user):
# common function to save the two sections data in answer table 
    answer=None
    for ques in sorted(quest_ids):
        question = Question.objects.get_or_none(id = int(ques))
#        if question.slug != "report_type" and question.slug != "report_duration" :
        answer, created = Answer.objects.get_or_create(question =question,
            content_type = ContentType.objects.get_for_model(project_report),object_id = project_report.id,user = user )
        
        if request.FILES.get(question.slug+'_'+str(question.id)) and (question.qtype == 'F' or question.qtype == 'API'):
            answer.attachment_file = request.FILES.get(question.slug+'_'+str(question.id)) 
            answer.description = 'cover image' if question.slug == 'cover_image' else 'Logos'
            answer.save()
        elif question.slug == 'report_duration' or question.slug == 'project_duration':
            start_date = data.get(question.slug+'_start'+'_'+str(question.id))
            end_date = data.get(question.slug+'_end'+'_'+str(question.id))
            answer.text = str(start_date)+' TO '+str(end_date)
            answer.save()
        elif question.qtype != 'F' and question.qtype != 'API':
            answer.text = data.get(question.slug+'_'+str(question.id))
            answer.save()
    return answer

def report_section_form(request):
    # to save the two sections cover page and project summary page data
    report_id = request.GET.get('report_id')
    image_url = PMU_URL
    quest_names=[]
    project_slug = request.GET.get('project_slug')
    user_id = request.session.get('user_id')
    user = UserProfile.objects.get_or_none(user_reference_id = user_id)
    project = Project.objects.get_or_none(slug = project_slug)
    report_obj = ProjectReport.objects.get_or_none(id = report_id)
    # to get the questions that are taged to the cover and project summary page
    quest_list = Question.objects.filter(active=2,block__block_type = 0)
    for i in quest_list:
        if i.slug == 'report_duration' or i.slug == 'project_duration':
            quest_names.append(i.slug+'_start_'+str(i.id))
            quest_names.append(i.slug+'_end_'+str(i.id))
        else:
            quest_names.append(i.slug+'_'+str(i.id))
#    quest_names = set(i.slug+'_'+str(i.id) for i in quest_list)# to get the question names with the ids so that to save the data 
    if not report_obj:
        report_obj = ProjectReport.objects.get_or_none(id = request.POST.get('report_id'))
    if request.method == 'POST' or request.method == 'FILES':
        data = request.POST
        project_obj = Project.objects.get_or_none(slug = data.get('project_slug'))
        project_report = ProjectReport.objects.get_or_none(id = data.get('report_id'))
        
        form_keys = set(data.keys())|set(request.FILES.keys())# to get the keys of the form so that to comapre the questions and then save
        final_ques = set(quest_names) & form_keys# Getting the questions that are common in form data and the questions tagged to that sections
        quest_ids = [i.split('_')[-1] for i in final_ques if i.split('_')]# Splitting the qname and ids so that to loop and save the answers for the particular question which is entered
        section_answer_saved = save_section_answers(quest_ids,project_report,request,data,user)
    return (locals())


from budgetmanagement.common_method import key_parameter_chart
from projectmanagement.views import parameter_pie_chart,get_timeline_process
from budgetmanagement.manage_budget import get_budget_quarters,tanchesamountlist
def html_to_pdf_view(request):
    # this function is to generate pdf with css and images.
    # here we are passing same variables which we are sending in report_detail function
    project_slug = request.GET.get('slug')
    image_url = PMU_URL
    project_report_id = request.GET.get('report_id')
    answer_list ={}
    answer = ''
    contents,quarters,number_dict = get_index_contents(project_slug,project_report_id)
    for key, value in sorted(contents.iteritems(), key=lambda (k,v): (v,k)):
        contents[key]=value
    project = Project.objects.get_or_none(slug = project_slug)
    parameter_obj = ProjectParameter.objects.filter(active= 2,project=project,parent=None)
    # calling function to get JSON data for pie chart display
    master_pip,master_pin,pin_title_name,pip_title_name,number_json,master_sh = parameter_pie_chart(parameter_obj)
    report_obj = ProjectReport.objects.get_or_none(id=project_report_id)
    report_quarter = QuarterReportSection.objects.filter(project=report_obj).order_by('quarter_type')
    # mapping view is to show funder and implementation partner relation
    mapping_view = ProjectFunderRelation.objects.get_or_none(project=project)
    budgetobj = Budget.objects.latest_one(project = project,active=2)
    budget_period = ProjectBudgetPeriodConf.objects.filter(project = project,budget = budgetobj,active=2).values_list('row_order', flat=True).distinct()
    quarter_list = get_budget_quarters(budgetobj)
    report_quest_list = Question.objects.filter(active=2,block__block_type = 0)
    project_tranche_list = Tranche.objects.filter(project = project,active=2)
    tranche_amount = tanchesamountlist(project_tranche_list)
    planned_amount = tranche_amount['planned_amount']
    actual_disbursed_amount = tranche_amount['actual_disbursed_amount']
    recommended_amount = tranche_amount['recommended_amount']
    utilized_amount = tranche_amount['utilized_amount']
    projectreportobj = ProjectReport.objects.get_or_none(id=project_report_id)
    previousquarter_list,currentquarter_list,futurequarter_list = get_quarters(projectreportobj)
    # for basic details of project report we are sending all fields in dictionary 
    answer_list = report_question_list(report_quest_list,report_obj,project)
    # here we are sending/rendering all variable to generate PDF 
    html_string = render_to_string('report/new-pdf.html', {
        'answer_list':answer_list,'answer':answer,'previousquarter_list':previousquarter_list,
        'currentquarter_list':currentquarter_list,'futurequarter_list':futurequarter_list,
        'utilized_amount':utilized_amount,'recommended_amount':recommended_amount,
        'actual_disbursed_amount':actual_disbursed_amount,'planned_amount':planned_amount,
        'quarter_list':quarter_list,'budget_period':budget_period,'image_url':image_url,
        'project':project,'report_quarter':report_quarter,'report_obj':report_obj,'contents':contents,
        'quarters':quarters})

    html = HTML(string=html_string)
    # first we are writing new PDF and sending request to download file in pdf format
    from pmu.settings import BASE_DIR
    import datetime
    dd = datetime.datetime.today()
    file_name = project.name +'_' +dd.strftime('%d_%m_%Y_%s') +".pdf"
    html.write_pdf(target=BASE_DIR + '/static/pdf-reports/'+file_name);
    fs = FileSystemStorage()
    with fs.open(BASE_DIR +'/static/pdf-reports/'+ file_name) as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=file_name'
        return response

    return response

def get_org_report_logo(answer_obj,ques,report_obj):
    answer=''
    from projectmanagement.templatetags import urs_tags
    org_logo,ngo_logo = urs_tags.get_org_logo(report_obj.project)
    answer = "/static/img/GoodCSR_color_circle.png"
    if str(ques.slug) == "client_logo":
        if org_logo:
            answer = org_logo
        else :
            answer = "/static/img/GoodCSR_color_circle.png"
    elif str(ques.slug) == "logos":
        if ngo_logo:
            answer = ngo_logo
        else:
            answer = "/static/img/GoodCSR_color_circle.png"
    return answer


def report_question_list(report_quest_list,report_obj,project):
    answer_list = {}
    image_url = PMU_URL
    for ques in report_quest_list:
        answer_obj = Answer.objects.get_or_none(question =ques,
                        content_type = ContentType.objects.get_for_model(report_obj),object_id = report_obj.id)
        if answer_obj and (ques.qtype == 'T' or ques.qtype == 'APT' or ques.qtype == 'ck'):
            answer = answer_obj.text
        elif answer_obj and (ques.qtype == 'F' or ques.qtype == 'API') and answer_obj.attachment_file:
            answer = image_url + '/' + answer_obj.attachment_file.url
        elif answer_obj and (ques.qtype == 'F' or ques.qtype == 'API') and answer_obj.attachment_file == '' :
            answer = get_org_report_logo(answer_obj,ques,report_obj)
        else:
            answer = ''
        answer_list[str(ques.slug)] = answer
    return answer_list

def report_detail(request):
# to display the details in the view report of the genreated report
    slug = request.GET.get('slug')
    image_url = PMU_URL
    report_id = request.GET.get('report_id')
    pdf_key = int(request.GET.get('key'))
    answer_list ={}
    answer = ''
    contents,quarters,number_dict = get_index_contents(slug,report_id)
    for key, value in sorted(contents.iteritems(), key=lambda (k,v): (v,k)):
        contents[key]=value
    project = Project.objects.get_or_none(slug = slug)
    parameter_obj = ProjectParameter.objects.filter(active= 2,project=project,parent=None)
    # calling function to get JSON data for pie chart display
    master_pip,master_pin,pin_title_name,pip_title_name,number_json,master_sh = parameter_pie_chart(parameter_obj)
    report_obj = ProjectReport.objects.get_or_none(project=project,id=report_id)
    report_quarter = QuarterReportSection.objects.filter(project=report_obj).order_by('id')
    # mapping view is to show funder and implementation partner relation
    mapping_view = ProjectFunderRelation.objects.get_or_none(project=project)
    budgetobj = Budget.objects.latest_one(project = project,active=2)
    budget_period = ProjectBudgetPeriodConf.objects.filter(project = project,budget = budgetobj,active=2).values_list('row_order', flat=True).distinct()
    quarter_list = get_budget_quarters(budgetobj)
    cover_image = Attachment.objects.get_or_none(description__iexact = 'cover image',\
        content_type = ContentType.objects.get_for_model(report_obj),object_id = report_id)
    location = ProjectLocation.objects.filter(object_id=project.id)
    quest_list = Question.objects.filter(active=2,block__block_type = 0)
    tranche_list = Tranche.objects.filter(project = project,active=2)
    tranche_amount = tanchesamountlist(tranche_list)
    planned_amount = tranche_amount['planned_amount']
    actual_disbursed_amount = tranche_amount['actual_disbursed_amount']
    recommended_amount = tranche_amount['recommended_amount']
    utilized_amount = tranche_amount['utilized_amount']
    projectreportobj = ProjectReport.objects.get_or_none(id=report_id)
    previousquarter_list,currentquarter_list,futurequarter_list = get_quarters(projectreportobj)
    # for basic details of project report we are sending all fields in dictionary 
    answer_list = report_question_list(quest_list,report_obj,project)
    if pdf_key == 1:
        return render(request,'report/report-template.html',locals())
    else:
        return render(request,'report/report-template_pdf.html',locals())

def get_quarter_report_logic(projectobj):
    ''' common functionality to get the start date,end date and no of quarter'''
    sd = projectobj.start_date
    projectobj_enddate = projectobj.end_date
    if sd.day >= 15:
        year = sd.year+1 if sd.month == 12 else sd.year
        month =  1 if sd.month == 12 else sd.month+1
        sd = sd.replace(day=01,month = month,year=year)
    elif sd.day < 15:
        sd = sd.replace(day=01,month = sd.month,year=sd.year)
    ed = projectobj.end_date
    no_of_quarters = math.ceil(float(((ed.year - sd.year) * 12 + ed.month - sd.month))/3)
    output_data = {'sd':sd,'projectobj_enddate':projectobj_enddate,
                   'ed':ed,'no_of_quarters':no_of_quarters}
    return output_data

import pytz
def get_quarters(projectobj):
    ''' To get the quarter list i this format 2017-10-01 to 2017-12-31 '''
    import datetime
    from datetime import datetime
    data = get_quarter_report_logic(projectobj)
    report_start_date = data['sd']
    projectobj_enddate = data['projectobj_enddate']
    no_of_quarters = data['no_of_quarters']
    report_end_date = data['ed']
    report_start_date = datetime.strptime(str(report_start_date)[:19], '%Y-%m-%d %H:%M:%S')
    report_end_date = datetime.strptime(str(report_end_date)[:19], '%Y-%m-%d %H:%M:%S')
    previousquarter_list = {}
    currentquarter_list = {}
    futurequarter_list = {}
    project = projectobj.project
    budget_obj = Budget.objects.get_or_none(project=project)
    if budget_obj:
        from budgetmanagement.manage_budget import get_budget_quarters
        
        budget_quarters = get_budget_quarters(budget_obj)
        for i,k in budget_quarters.iteritems():
            sd = k.split('to')[0]
            ed = k.split('to')[1]
            sd = sd.strip()
            ed = ed.strip()
            sd = datetime.strptime(sd, '%Y-%m-%d')
            ed = datetime.strptime(ed , '%Y-%m-%d')
#            projectobj_enddate = datetime.strptime(str(projectobj_enddate)[:19], '%Y-%m-%d %H:%M:%S')
#            if ed > projectobj_enddate:
#                ed = projectobj_enddate
            if report_start_date.date() >= sd.date() and report_end_date.date() <= ed.date():
                currentquarter_list.update({i:str(sd.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d"))+" to "+str(ed.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d"))})
            elif sd > report_start_date and ed > report_start_date:
                futurequarter_list.update({i:str(sd.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d"))+" to "+str(ed.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d"))})
            elif sd < report_start_date and ed < report_start_date:
                previousquarter_list.update({i:str(sd.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d"))+" to "+str(ed.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d"))})
    print budget_quarters,report_start_date,report_end_date
    return previousquarter_list,currentquarter_list,futurequarter_list

def get_quarter_report(request,itemlist,quarter):
    result = {}
    for line in itemlist:
        if str(quarter) == line.split('_')[2]:
            line_list = line.split('_')
            name = line.split('_')[0]
            result.update({name:request.POST.get(line)})
    return result


def display_blocks(request):
# this is to get the two blocks cover page and project summary page so that to display the questions in dynamic
    project_slug = request.GET.get('slug')
    report_id = request.GET.get('report_id')
    survey = Survey.objects.get(id=1)
    image_url = PMU_URL
    block1 = Block.objects.get_or_none(survey=survey,name__iexact = 'Cover Page',block_type=0)
    block2 = Block.objects.get_or_none(survey=survey,name__iexact = 'Project Summary Sheet',block_type=0)
    project_report = ProjectReport.objects.get_or_none(id=report_id)
    project = Project.objects.get_or_none(slug=project_slug)
    mapping_view = ProjectFunderRelation.objects.get_or_none(project=project)
    return (locals())
    

#this is the actual report saving we are using 

def get_milestone_parameterlist(request,previous_itemlist,quarterreportobj,projectreportobj,user_obj,quarter):
    milestone_list = []
    pic_list = []
    parameter_list = []
    for line in previous_itemlist:
        if str(quarter) == line.split('_')[2]:
            line_list = line.split('_')
            if len(line_list) == 5:
                question_id = line_list[3]
                answer_dict = {
                'quarter':quarterreportobj,
                'question':Question.objects.get_or_none(id=int(question_id)),
                'text':request.POST.get(line),
                'content_type':ContentType.objects.get_for_model(projectreportobj),
                'object_id':projectreportobj.id,
                'user':user_obj,
                }
                answerobj = Answer.objects.get_or_none(question__id=question_id,quarter=quarterreportobj)
                if not answerobj:
                    answer = Answer.objects.create(**answer_dict)
                else:
                    answerobj.text = request.POST.get(line)
                    answerobj.save()
            elif len(line_list) == 7:
                milestone_list.append(line)
            elif len(line_list) == 8 and line_list[6] != "parameter":
                pic_list.append(line)
            else:
                parameter_list.append(line)
    return milestone_list,parameter_list,pic_list

def get_report_based_quarter(request,quarter_list,projectreportobj,previous_itemlist):
    milestone_list=[]
    parameter_list=[]
    pic_list=[]
    quarterreportobj =None
    for quarter,value in quarter_list.items():
        present_quarter = previous_itemlist[0]
        quarter_type = present_quarter.split('_')[1]
        if str(quarter) == present_quarter.split('_')[2]:
            budget_period = value
            start_date = budget_period.split('to')[0].rstrip()
            end_date = budget_period.split('to')[1].lstrip()
            quarter_report_dict = {
            'project':projectreportobj,
            'quarter_type':quarter_type,
            'start_date':start_date,
            'end_date':end_date,
            'quarter_order':quarter,
            }
            quarterreportobj = QuarterReportSection.objects.get_or_none(project=projectreportobj,quarter_type = quarter_type,quarter_order = quarter )
            if not quarterreportobj:
                quarterreportobj = QuarterReportSection.objects.create(**quarter_report_dict)
            user_obj = UserProfile.objects.get_or_none(user_reference_id = request.session.get('user_id'))
            milestone_list,parameter_list,pic_list = get_milestone_parameterlist(request,previous_itemlist,quarterreportobj,projectreportobj,user_obj,quarter)
    return milestone_list,parameter_list,pic_list,quarterreportobj

def quarter_image_save(request,milestoneobj,projectobj,pic_count,pic_list,quarterreportobj):
#    Common functionality to save the images
    imageobj = None
    milestone_images = {}
    act_count = [i[0].split('_')[-1] for i in request.POST.items() if i[0].startswith('Picture')]
    quest_list = Question.objects.filter(slug='upload-picture').values_list('id',flat=True)
    add_section = request.POST.get('add_section')# this is to know whether it is add or edit page
    
    for j in pic_count :
        milestone_images = {}
        name1 = []
        for pic in pic_list:
            pic_length_list = pic.split('_')
            pic_quest_id = pic.split('_')[3]
            name = pic_length_list[0].split('-')
            name1 = pic_length_list[0].split('-')
            image_id = pic_length_list[-1]
            if int(pic_quest_id) in quest_list:
                milestone_images.update({name[0].lower():request.FILES.get(pic)})
            else:
                milestone_images.update({name[0].lower():request.POST.get(pic)})


        user_obj = UserProfile.objects.get_or_none(user_reference_id = request.session.get('user_id'))
        
        image_dict = {
                'created_by' : user_obj,
                'attachment_file':milestone_images.get('upload picture',''),
                'description' : milestone_images.get('picture description',''), 
                'name' : projectobj.name,
                'attachment_type' : 1,
                'content_type' : ContentType.objects.get_for_model(milestoneobj),
                'object_id' : milestoneobj.id
        }
        if int(add_section) == 0 or len(name1) == 2:
            imageobj = Attachment.objects.create(**image_dict)
        else:
            imageobj = Attachment.objects.get_or_none(id=int(image_id))
            if image_dict.get('attachment_file'):
                imageobj.attachment_file = image_dict.get('attachment_file') 
            imageobj.description = image_dict.get('description')
            imageobj.save()
    return imageobj

def get_activities_list(request,quarterreportobj):
#    to get activities or milestones list
    if int(quarterreportobj.quarter_type) == 1:
        act_count = [i[0].split('_')[-1] for i in request.POST.items() if i[0].startswith('Milest')]
        # to get the last digit of the add more activity/milestone so that to loop and check condition
    else:
        act_count = [i[0].split('_')[-1] for i in request.POST.items() if i[0].startswith('Activi')]
    return act_count

def report_milestone_save(request,quarterreportobj,add_section,name1,mile_id,result):
#    this is to save the milestone object
    if int(quarterreportobj.quarter_type) == 1:
        name = result.get('milestone','')
        description = result.get('about milestone','')
    else:
        name = result.get('activity','')
        description = result.get('about the activity','')
    # here checking for add or edit so that to get the ReportMilestoneActivity object
    # name1 length > 1 then it is the add more of activity/milestone in edit to specify that whether it is edit add more 
    # In edit add more to the name we are appending "-1" so that to know it is add more in edit form
    # for example name = Activity-1_2_0_40_1_1_3 then name.split('-') we will get ['Activity','1'] based on the length of this 
    # we will make sure it is of add more from edit and create a new object for that added activity/milestone
    if int(add_section) == 0 or len(name1) == 2:
        milestoneobj = ReportMilestoneActivity.objects.create(quarter=quarterreportobj,name=name,description=description)
    else:
        milestoneobj = ReportMilestoneActivity.objects.get_or_none(id=int(mile_id))
        if milestoneobj:
            milestoneobj.name = name
            milestoneobj.description=description
            milestoneobj.active = 2
            milestoneobj.save()
    return milestoneobj



def milestone_activity_save(request,milestone_list,obj_count_list,pic_list,projectreportobj,quarterreportobj,projectobj):
    mil_activity_count = obj_count_list.get('milestone_count')
    pic_count = obj_count_list.get('milestone_pic_count')
    milestoneobj = ReportMilestoneActivity.objects.filter(quarter=quarterreportobj,active=2)
    add_section = request.POST.get('add_section')# this is to know whether it is add or edit page
    for milestone in milestoneobj:
        milestone.active = 0
        milestone.save()
    act_count = get_activities_list(request,quarterreportobj)
    for i in act_count:
        result = {}
        name1 = []
        for mile_attribute in milestone_list:
            mile_length_list =  mile_attribute.split('_')
            if i == mile_length_list[-1] and len(mile_length_list) == 7:
                name = mile_length_list[0].split('-')
                name1 = mile_length_list[0].split('-')
                mile_id = mile_length_list[-1]
                parent_milestone_question = Question.objects.get(id=mile_length_list[3]).parent
                result.update({name[0].lower():request.POST.get(mile_attribute)})
                pic_list1 =[p for p in pic_list if p.split('_')[-2] == i]
        milestoneobj = report_milestone_save(request,quarterreportobj,add_section,name1,mile_id,result)
        imageobj = quarter_image_save(request,milestoneobj,projectobj,pic_count,pic_list1,quarterreportobj)
    user_obj = UserProfile.objects.get_or_none(user_reference_id = request.session.get('user_id'))
    milestone_ids = ReportMilestoneActivity.objects.filter(quarter=quarterreportobj,active=2).values_list("id",flat=True)
    milestone_ids = map(int,milestone_ids)
    milestone_answer_dict = {
            'quarter':quarterreportobj,
            'question':Question.objects.get_or_none(id=int(parent_milestone_question.id)),
            'inline_answer':milestone_ids,
            'content_type':ContentType.objects.get_for_model(projectreportobj),
            'object_id':projectreportobj.id,
            'user':user_obj,
            }
    answer =  Answer.objects.get_or_none(question = milestone_answer_dict.get('question'),quarter=quarterreportobj)
    if answer:
        answer.inline_answer = milestone_ids
        answer.save()
    else:
        answer = Answer.objects.create(**milestone_answer_dict)
    return answer

def report_parameter_save(request,parameter_count,parameter_list,projectreportobj,quarterreportobj):
    add_section = request.POST.get('add_section')
    para_detail = [i[0].split('_')[-1] for i in request.POST.items() if i[0].startswith('Parameter')]
    for k in sorted(para_detail):
        parameter_result = {}
        for parameter in parameter_list:
            param_list =  parameter.split('_')
            if len(param_list) == 8 and k == param_list[-1]:
                name = param_list[0].split('-')
                name1 = param_list[0].split('-')
                parameter_id = param_list[-1]
                parent_paramter_question = Question.objects.get(id=param_list[3]).parent
                parameter_result.update({name[0].lower():request.POST.get(parameter)})
        if int(add_section) == 0 or len(name1) == 2:
            reportparamterobj = ReportParameter.objects.create(quarter = quarterreportobj,keyparameter=ProjectParameter.objects.get_or_none(id=int(parameter_result['parameter selection'])),description = parameter_result['about parameter'])
        else:
            reportparamterobj = ReportParameter.objects.get(id=int(parameter_id))
            reportparamterobj.keyparameter = ProjectParameter.objects.get_or_none(id=int(parameter_result['parameter selection']))
            reportparamterobj.description = parameter_result['about parameter']
            reportparamterobj.save()
    user_obj = UserProfile.objects.get_or_none(user_reference_id = request.session.get('user_id'))
    parameter_ids = ReportParameter.objects.filter(quarter = quarterreportobj).values_list("id",flat=True)
    parameter_ids = map(int,parameter_ids)
    parameter_answer_dict = {
            'quarter':quarterreportobj,
            'question':Question.objects.get_or_none(id=int(parent_paramter_question.id)),
            'inline_answer':parameter_ids,
            'content_type':ContentType.objects.get_for_model(projectreportobj),
            'object_id':projectreportobj.id,
            'user':user_obj,
            }
    answer =  Answer.objects.get_or_none(question = parameter_answer_dict.get('question'),quarter=quarterreportobj)
    if answer:
        answer.inline_answer = parameter_ids
        answer.save()
    else:
        answer = Answer.objects.create(**parameter_answer_dict)
    return answer

def saving_of_quarters_section(request):
    slug = request.GET.get('slug')
    projectobj = Project.objects.get_or_none(slug=slug)
    projectreportobj = ProjectReport.objects.get_or_none(id=request.POST.get('report_id'))
    projectobj = projectreportobj.project
    previousquarter_list,currentquarter_list,futurequarter_list = get_quarters(projectreportobj)
#    to save the previous quarter updates:
    quarter_list = previousquarter_list
    previous_itemlist = [str(k) for k,v in request.POST.items() if '_1_' in str(k) if k.split('_')[1]=='1']
    previous_itemlist.extend([str(k) for k,v in request.FILES.items() if '_1_' in str(k) if k.split('_')[1]=='1'])
    if previous_itemlist:
        milestone_list,parameter_list,pic_list,quarterreportobj = get_report_based_quarter(request,quarter_list,projectreportobj,previous_itemlist)
        quarter_number = previous_itemlist[0].split('_')[2]
        milestone_count = request.POST.get('milestone_count_'+str(quarter_number)+"_"+str(1),0)
        milestone_pic_count = request.POST.get('milestone-pic-count_1',0)
        parameter_count = request.POST.get('parameter_count_1',0)
        if milestone_count > 0:
            obj_count_list = {'milestone_pic_count':milestone_pic_count,'milestone_count':milestone_count,}
            answer = milestone_activity_save(request,milestone_list,obj_count_list,pic_list,projectreportobj,quarterreportobj,projectobj)
# clients requirement not to provide paramerter selection in previous quarter list so commented
# end of parameter saving function
#    to save the Current quarter updates:
    quarter_list = currentquarter_list
    
    current_itemlist = [str(k) for k,v in request.POST.items() if '_2_' in str(k) if k.split('_')[1]=='2']
    current_itemlist.extend([str(k) for k,v in request.FILES.items() if '_2_' in str(k) if k.split('_')[1]=='2'])
    if current_itemlist:
        milestone_list,parameter_list,pic_list,quarterreportobj = get_report_based_quarter(request,quarter_list,projectreportobj,current_itemlist)
        quarter_number = current_itemlist[0].split('_')[2]
        activity_count = request.POST.get('activity_count_'+str(quarter_number)+"_"+str(1),0)
        activity_pic_count = request.POST.get('activity-pic-count_1',0)
        parameter_count = request.POST.get('current_parameter_count_1',0)
        if activity_count > 0:
            obj_count_list = {'milestone_pic_count':activity_pic_count,'milestone_count':activity_count,}
            answer = milestone_activity_save(request,milestone_list,obj_count_list,pic_list,projectreportobj,quarterreportobj,projectobj)
        if parameter_count > 0:
            answer = report_parameter_save(request,parameter_count,parameter_list,projectreportobj,quarterreportobj)
#    to save the next quarter updates:
    quarter_list = futurequarter_list
    next_itemlist = [str(k) for k,v in request.POST.items() if '_3_' in str(k) if k.split('_')[1]=='3']
    if next_itemlist:
        milestone_list,parameter_list,pic_list,quarterreportobj = get_report_based_quarter(request,quarter_list,projectreportobj,next_itemlist)
    return projectreportobj



def finalreportdesign(request):
    slug = request.GET.get('slug')
    report_id = request.GET.get('report_id')
    key = request.GET.get('key')
    #to display the cover page and summary page sections calling the functions by passing request #STARTS)
    locals_list = display_blocks(request)
    # end of the display cover page and summary #ENDS
    projectobj = Project.objects.get_or_none(slug=slug)
    budgetobj = Budget.objects.latest_one(project = projectobj,active=2)
    budget_period = ProjectBudgetPeriodConf.objects.filter(project = projectobj,budget = budgetobj,active=2).values_list('row_order', flat=True).distinct()
#    trancches detail 
    tranche_list = Tranche.objects.filter(project = projectobj,active=2)

    tranche_amount = tanchesamountlist(tranche_list)
    planned_amount = tranche_amount['planned_amount']
    actual_disbursed_amount = tranche_amount['actual_disbursed_amount']
    recommended_amount = tranche_amount['recommended_amount']
    utilized_amount = tranche_amount['utilized_amount']
#     tranches detail ends 
    projectreportobj = ProjectReport.objects.get_or_none(id=request.GET.get('report_id'))#based on report id filter the project report obj
    previousquarter_list,currentquarter_list,futurequarter_list = {},{},{}
    if projectreportobj:
        previousquarter_list,currentquarter_list,futurequarter_list = get_quarters(projectreportobj)
#      timeline progress 
    image = PMU_URL
#      timeline progress ends 
    previous_len = len(previousquarter_list)+1
    current_len = len(currentquarter_list)+1
    future_len = previous_len+current_len
    project_paramterlist = ProjectParameter.objects.filter(project__slug=slug,parent=None,active=2)
    previous_questionlist = Question.objects.filter(active = 2,block__slug="previous-quarter-update",parent=None).order_by("order")
    current_questionlist = Question.objects.filter(active = 2,block__slug="current-quarter-update",parent=None).order_by("order")
    next_questionlist  = Question.objects.filter(active = 2,block__slug="next-quarter-update",parent=None).order_by("order")
    if request.method == "POST" or request.FILES:
        slug = request.POST.get('slug')
        key = request.POST.get('key')
        projectobj = Project.objects.get_or_none(slug=slug)#based on slug filter the project obj
        projectreportobj = ProjectReport.objects.get_or_none(id= request.POST.get('report_id'))
        div_id = request.POST.get('div_id')
        #to save the two sections data based the save of two sections calling the report_section_form()
        cover_page_locals = report_section_form(request)
            #        to save the quarter reports
        projectreportobj = saving_of_quarters_section(request)
        projectobj = projectreportobj.project
        # redirection to the same page of the form #STARTS
        if key == 'edit_template':
            return HttpResponseRedirect('/report/final/design/?slug='+projectobj.slug+'&report_id='+str(projectreportobj.id)+'&key='+str(key))
        elif key == 'removed_template':
            return HttpResponseRedirect('/report/final/design/?slug='+projectobj.slug+'&report_id='+str(projectreportobj.id)+'&key='+str(key))
        else:
            return HttpResponseRedirect('/report/final/design/?slug='+projectobj.slug+'&report_id='+str(projectreportobj.id)+'&div_id='+str(int(div_id)+1))               
        # ENDS to redirection  
    if key == 'edit_template':
        return render(request,'report/forms-single.html',locals())
    elif key == 'removed_template':
        return render(request,'report/removed-questions.html',locals())
    else:
        return render(request,'report/final_report.html',locals())

from collections import OrderedDict
def get_index_contents(slug,report_id):
# to get the index contents dynamically by using a dictionay passing the contents
    contents = OrderedDict()
    index={}
    quarters = {}
    number_dict ={}
    project = Project.objects.get_or_none(slug=slug)
    report_obj = ProjectReport.objects.get_or_none(id=report_id)
    # by using get_quarters() function getting the previous,current and next quarters list
    previousquarter_list,currentquarter_list,futurequarter_list = get_quarters(report_obj)
    # based on the answer object created to the report,if answer object is created to that report
    # then we will display the contents which are present
    cover_summary_answers = answer=Answer.objects.filter(question__block__block_type=0,
        content_type = ContentType.objects.get_for_model(report_obj),object_id=report_id)
    # if answer object is present for the particular report then add "About the Project" to the dict
    if cover_summary_answers:
        contents['1']= 'About the project'
        quarters['About the project'] = ''
        # if previous quarter then add to contents dict and in quarters dict give the list of quarters to that previous quarter
        # so that we can render the quarters based on the name of the content and iterate it
        # same way for current and next quarters is done
        if previousquarter_list:
            contents['2'] = 'Previous Quarter Updates'
            quarters['Previous Quarter Updates'] = previousquarter_list
        if currentquarter_list:
            contents['3'] = 'Current Quarter Updates'
            quarters['Current Quarter Updates'] = currentquarter_list
        if futurequarter_list:
            contents['4'] = 'Next Quarter Updates'
            import operator
            # here we getting all next quarter so we taking first quarter 
            sorted_futurequarter_list = dict([sorted(futurequarter_list.items(), key=operator.itemgetter(1))[0]])
            quarters['Next Quarter Updates']=sorted_futurequarter_list
        contents['5'] = "Annexure"
        quarters['Annexure']=''
        number_dict = {0:"First",1:"Second",2:"Third",3:"Fourth",4:"Fifth",5:"Sixth",6:"Seventh",7:"Eigth",8:"Ninth",9:"Tenth"}
    for key, value in sorted(contents.iteritems(), key=lambda (k,v): (v,k)):
        contents[key]=value
    return contents,quarters,number_dict

from ast import literal_eval

def remove_milesact_child(ques_obj,ids):
    removed_list = []
    child_ques = Question.objects.filter(parent = ques_obj.parent).values_list('id',flat=True)
    if ques_obj.slug == 'milestone-name' or ques_obj.slug == 'activity-name':
        removed_list = [int(i) for i in child_ques]
    elif ques_obj.slug == 'upload-picture':
        removed_list.append(ids)
        removed_list.append(Question.objects.get_or_none(slug = 'picture-description').id)
        removed_list.append(ids)
    else:
        removed_list.append(ids)
    return removed_list

def save_removed_fields(request):
    
    quest_ids_list = []
    removed_list=[]
    ids = literal_eval(request.GET.get('id'))
    url = str(request.GET.get('redirect_url'))
    report_id = literal_eval(request.GET.get('report_id'))
    report_obj = ProjectReport.objects.get_or_none(id=report_id)
    block_type = literal_eval(request.GET.get('block_type'))
    object_id = request.GET.get('object_id')
    period = request.GET.get('period')# this is to get the period for particular quarter so that to differentiate
    ques_obj = Question.objects.get_or_none(id=ids)
    if int(ques_obj.block.code) in [1,2]:
        removed_ques, created = RemoveQuestion.objects.get_or_create(quarter_report= report_obj,block_type=block_type)
    else:
        if object_id != 'None':

            quarter_report = QuarterReportSection.objects.get_or_none(id=object_id)
            removed_ques, created = RemoveQuestion.objects.get_or_create(quarter_report= report_obj,
                block_type = block_type,quarter_period = period)
            removed_ques.content_type = ContentType.objects.get_for_model(quarter_report)
            removed_ques.object_id = literal_eval(object_id)
            removed_ques.save()
        else:
            removed_ques,created = RemoveQuestion.objects.get_or_create(quarter_report= report_obj,
                block_type = block_type,quarter_period = period)
        quest_ids_list = remove_milesact_child(ques_obj,ids)
    if created:
#        quest_ids_list.append(ids)
        removed_ques.text = quest_ids_list
    else:
        removed_list = literal_eval(removed_ques.text) if removed_ques.text else []
#        removed_list.append(ids)
        removed_list=quest_ids_list        
        removed_ques.text = sorted(removed_list)
    removed_ques.save()
    return HttpResponseRedirect(url)
    

def save_added_fields(request):
    ids = literal_eval(request.GET.get('id'))
    url = str(request.GET.get('redirect_url'))
    remove_quest_obj = RemoveQuestion.objects.get_or_none(id=int(request.GET.get('remove_obj')))
    if remove_quest_obj:
        ques_list = eval(remove_quest_obj.text)
        if ids in ques_list:
            ques_list.remove(ids)
            remove_quest_obj.text = ques_list
            remove_quest_obj.save()
    return HttpResponseRedirect(url)
