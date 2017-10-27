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
from budgetmanagement.models import *
from budgetmanagement.manage_budget import get_budget_logic
from django.shortcuts import redirect
from pmu.settings import PMU_URL

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
            budget_start_date = budget_quarters.get(0).split(' to ')[0] 
            project_obj = Project.objects.get_or_none(slug = data.get('project_slug'))
            quarter_ids = data.get('quarter_type')
            dates = budget_quarters[int(quarter_ids)]
            dates_list = dates.split(' to ')
            budget_end_date = dates_list[1] if dates_list else '' 
            project_report ,created = ProjectReport.objects.get_or_create(project = project_obj,created_by = user,\
                report_type = data.get('report_type'),start_date  = budget_start_date,
                name = project_obj.name,end_date = budget_end_date)
            if created:
                return HttpResponseRedirect('/report/final/design/?slug='+data.get('project_slug')+'&report_id='+str(project_report.id))
            else:
                project_report.save()
                quarter_msg = "Already Report is generated to this Quarter"
#            project_report.end_date = dates_list[1] if dates_list else ''
#            project_report.save()
            
    else :
        msg = "Budget is not created"
    return render(request,'report/report-form.html',locals())

def report_listing(request):
# listing of the generated reports in the lisiting page
    slug =  request.GET.get('slug')
    project = Project.objects.get_or_none(slug = request.GET.get('slug'))
    report_obj = ProjectReport.objects.filter(project=project)
    return render(request,'report/listing.html',locals())

def save_section_answers(quest_ids,project_report,request,data,user):
# common function to save the two sections data in answer table 
    for ques in sorted(quest_ids):
        question = Question.objects.get_or_none(id = int(ques))
        if question.slug != "report_type" and question.slug != "report_duration" :
            answer, created = Answer.objects.get_or_create(question =question,
                content_type = ContentType.objects.get_for_model(project_report),object_id = project_report.id,user = user )
            if request.FILES.get(question.slug+'_'+str(question.id)) and (question.qtype == 'F' or question.qtype == 'API'):
                answer.attachment_file = request.FILES.get(question.slug+'_'+str(question.id)) 
                answer.description = 'cover image' if question.slug == 'cover_image' else 'Logos'
                answer.save()
            elif question.qtype != 'F' and question.qtype != 'API':
                answer.text = data.get(question.slug+'_'+str(question.id))
                answer.save()
    return answer

def report_section_form(request):
    # to save the two sections cover page and project summary page data
    report_id = request.GET.get('report_id')
    image_url = PMU_URL
    project_slug = request.GET.get('project_slug')
    user_id = request.session.get('user_id')
    user = UserProfile.objects.get_or_none(user_reference_id = user_id)
    project = Project.objects.get_or_none(slug = project_slug)
    report_obj = ProjectReport.objects.get_or_none(id = report_id)
    # to get the questions that are taged to the cover and project summary page
    quest_list = Question.objects.filter(active=2,block__block_type = 0)
    quest_names = set(i.slug+'_'+str(i.id) for i in quest_list)# to get the question names with the ids so that to save the data 
    if not report_obj:
        report_obj = ProjectReport.objects.get_or_none(id = request.POST.get('report_id'))
    if request.method == 'POST' or request.method == 'FILES':
        data = request.POST
        project_obj = Project.objects.get_or_none(slug = data.get('project_slug'))
        project_report = ProjectReport.objects.get_or_none(id = data.get('report_id'))
        form_keys = set(data.keys())|set(request.FILES.keys())# to get the keys of the form so that to comapre the questions and then save
        final_ques = quest_names & form_keys# Getting the questions that are common in form data and the questions tagged to that sections
        quest_ids = [i.split('_')[-1] for i in final_ques if i.split('_')]# Splitting the qname and ids so that to loop and save the answers for the particular question which is entered
        section_answer_saved = save_section_answers(quest_ids,project_report,request,data,user)
    return (locals())

from budgetmanagement.common_method import key_parameter_chart
from projectmanagement.views import parameter_pie_chart
from budgetmanagement.manage_budget import get_budget_quarters,tanchesamountlist
def report_detail(request):
# to display the details in the view report of the genreated report
    slug = request.GET.get('slug')
    image_url = PMU_URL
    report_id = request.GET.get('report_id')
    answer_list ={}
    answer = ''
    project = Project.objects.get_or_none(slug = slug)
    parameter_obj = ProjectParameter.objects.filter(active= 2,project=project,parent=None)
    master_pip,master_pin,pin_title_name,pip_title_name,number_json,master_sh = parameter_pie_chart(parameter_obj)
    report_obj = ProjectReport.objects.get_or_none(project=project,id=report_id)
    report_quarter = QuarterReportSection.objects.filter(project=report_obj)
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
    for question in quest_list:
        answer_obj = Answer.objects.get_or_none(question =question,
                        content_type = ContentType.objects.get_for_model(report_obj),object_id = report_obj.id)
        if answer_obj and (question.qtype == 'T' or question.qtype == 'APT'):
            answer = answer_obj.text 
        elif answer_obj and (question.qtype == 'F' or question.qtype == 'API') and answer_obj.attachment_file:
            answer = answer_obj.attachment_file.url 
        else:
            answer = ''
        answer_list[str(question.slug)] = answer
    return render(request,'report/report-template.html',locals())

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
#    return render(request,'report/report-display-section.html',locals())
    

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
            elif len(line_list) == 8 and line_list[6] == "parameter":
                parameter_list.append(line)
    return milestone_list,parameter_list,pic_list

def get_report_based_quarter(request,quarter_list,projectreportobj,previous_itemlist):
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

def quarter_image_save(request,milestoneobj,projectobj,pic_count,pic_list):
#    Common functionality to save the images
    imageobj = None
    for j in range(int(pic_count)):
        milestone_images = {}
        for pic in pic_list:
            pic_length_list = pic.split('_')
            if len(pic_length_list) == 8 and pic_length_list[-3] == str(j+1):
                name = pic_length_list[0]
                image_id = pic_length_list[-1]
                milestone_images.update({name.lower():request.POST.get(pic)})


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
        if int(image_id) == 0:
            imageobj = Attachment.objects.create(**image_dict)
        else:
            imageobj = Attachment.objects.get_or_none(id=int(image_id))
            imageobj.attachment_file = image_dict.get('attachment_file')
            imageobj.description = image_dict.get('description')
            imageobj.save()
    return imageobj

def milestone_activity_save(request,milestone_list,obj_count_list,pic_list,projectreportobj,quarterreportobj,projectobj):
    mil_activity_count = obj_count_list.get('milestone_count')
    pic_count = obj_count_list.get('milestone_pic_count')
    for i in range(int(mil_activity_count)):
        result = {}
        for mile_attribute in milestone_list:
            mile_length_list =  mile_attribute.split('_')
            if len(mile_length_list) == 7 and mile_length_list[-2] == str(i+1):
                name = mile_length_list[0]
                mile_id = mile_length_list[-1]
                parent_milestone_question = Question.objects.get(id=mile_length_list[3]).parent
                result.update({name.lower():request.POST.get(mile_attribute)})
        if quarterreportobj.quarter_type == 1:
            name = result.get('milestone','')
            description = result.get('about milestone','')
        else:
            name = result.get('activity','')
            description = result.get('about the activity','')
        if int(mile_id) == 0:
            milestoneobj = ReportMilestoneActivity.objects.create(quarter=quarterreportobj,name=name,description=description)
        else:
            milestoneobj = ReportMilestoneActivity.objects.get(id=int(mile_id))
            milestoneobj.name = name
            milestoneobj.description=description
            milestoneobj.save()
        imageobj = quarter_image_save(request,milestoneobj,projectobj,pic_count,pic_list)
    user_obj = UserProfile.objects.get_or_none(user_reference_id = request.session.get('user_id'))
    milestone_ids = ReportMilestoneActivity.objects.filter(quarter=quarterreportobj).values_list("id",flat=True)
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
    for k in range(int(parameter_count)):
        parameter_result = {}
        for parameter in parameter_list:
            param_list =  parameter.split('_')
            if len(param_list) == 8 and int(param_list[5]) == int(k)+1:
                name = param_list[0]
                parameter_id = param_list[-1]
                parent_paramter_question = Question.objects.get(id=param_list[3]).parent
                parameter_result.update({name.lower():request.POST.get(parameter)})
        if int(parameter_id) == 0:
            reportparamterobj = ReportParameter.objects.create(quarter = quarterreportobj,keyparameter=ProjectParameter.objects.get(id=int(parameter_result['parameter selection'])),description = parameter_result['about parameter'])
        else:
            reportparamterobj = ReportParameter.objects.get(id=int(parameter_id))
            reportparamterobj.keyparameter = ProjectParameter.objects.get(id=int(parameter_result['parameter selection']))
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
    if previous_itemlist:
        milestone_list,parameter_list,pic_list,quarterreportobj = get_report_based_quarter(request,quarter_list,projectreportobj,previous_itemlist)
        milestone_count = request.POST.get('milestone_count_1',0)
        milestone_pic_count = request.POST.get('milestone-pic-count_1',0)
        parameter_count = request.POST.get('parameter_count_1',0)
        if milestone_count > 0:
            obj_count_list = {'milestone_pic_count':milestone_pic_count,'milestone_count':milestone_count,}
            answer = milestone_activity_save(request,milestone_list,obj_count_list,pic_list,projectreportobj,quarterreportobj,projectobj)
        if parameter_count > 0:
            answer = report_parameter_save(request,parameter_count,parameter_list,projectreportobj,quarterreportobj)
#    to save the Current quarter updates:
    quarter_list = currentquarter_list
    current_itemlist = [str(k) for k,v in request.POST.items() if '_2_' in str(k) if k.split('_')[1]=='2']
    if current_itemlist:
        milestone_list,parameter_list,pic_list,quarterreportobj = get_report_based_quarter(request,quarter_list,projectreportobj,current_itemlist)
        activity_count = request.POST.get('activity_count_1',0)
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
    #to display the cover page and summary page sections calling the functions by passing request #STARTS)
    locals_list = display_blocks(request)
    # end of the display cover page and summary #ENDS
    projectobj = Project.objects.get_or_none(slug=slug)
    projectreportobj = ProjectReport.objects.get_or_none(id=request.GET.get('report_id'))#based on report id filter the project report obj
    previousquarter_list,currentquarter_list,futurequarter_list = {},{},{}
    if projectreportobj:
        previousquarter_list,currentquarter_list,futurequarter_list = get_quarters(projectreportobj)
    project_paramterlist = ProjectParameter.objects.filter(project__slug=slug,parent=None)
    previous_questionlist = Question.objects.filter(active = 2,block__slug="previous-quarter-update",parent=None).order_by("order")
    current_questionlist = Question.objects.filter(active = 2,block__slug="current-quarter-update",parent=None).order_by("order")
    next_questionlist = Question.objects.filter(active = 2,block__slug="next-quarter-update",parent=None).order_by("order")
    if request.method == "POST":
        slug = request.POST.get('slug')
        projectobj = Project.objects.get_or_none(slug=slug)#based on slug filter the project obj
        projectreportobj = ProjectReport.objects.get_or_none(id= request.POST.get('report_id'))
        #to save the two sections data based the save of two sections calling the report_section_form()#STARTS
        if request.POST.get('cover_page_save') or request.POST.get('project_summary_save'):
            cover_page_locals = report_section_form(request)
        # else the dynamic sections of the quarters are saved when that sections are made to be saved # ENDS
        else:
            #        to save the quarter reports
            projectreportobj = saving_of_quarters_section(request)
            projectobj = projectreportobj.project
        # redirection to the same page of the form #STARTS
        return HttpResponseRedirect('/report/final/design/?slug='+projectobj.slug+'&report_id='+str(projectreportobj.id))               
        # ENDS to redirection   
    return render(request,'report/final_report.html',locals())

