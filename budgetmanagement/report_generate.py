import requests,ast
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from media.models import Article,Section,ContactPersonInformation
from media.forms import ContactPersonForm
from django.template import loader
from projectmanagement.models import Project,UserProfile,ProjectFunderRelation


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
    name = request.POST.get('name')
    return render(request,'project/project_details.html',locals())
