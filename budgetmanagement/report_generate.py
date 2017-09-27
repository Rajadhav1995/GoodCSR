import requests,ast
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from media.models import Article,Section,ContactPersonInformation
from media.forms import ContactPersonForm
from django.template import loader
from projectmanagement.models import Project,UserProfile,ProjectFunderRelation
from budgetmanagement.models import *


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
    if request.method == 'POST':
        data = request.POST
        project_obj = Project.objects.get_or_none(slug = data.get('project_slug'))
        project_report = ProjectReport.objects.create(project = project_obj,created_by = user,\
            report_type = data.get('report_type'),name = project_obj.name)
        project_report.start_date = data.get('start_date')
        project_report.end_date = data.get('end_date')
        project_report.description = data.get('description')
        project_report.objective = data.get('objective')
        project_report.save()
    funder = request.POST.get('funder')
    total_budget = request.POST.get('total_budget')
    duration = request.POST.get('duration')
    beneficiaries_no = request.POST.get('beneficiaries_no')
    implementation_partner = request.POST.get('implementation_partner')
    
    return render(request,'project/project_details.html',locals())
