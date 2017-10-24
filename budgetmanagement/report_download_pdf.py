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

from budgetmanagement.common_method import key_parameter_chart
from projectmanagement.views import parameter_pie_chart

#import pdfkit
import csv
from reportlab.pdfgen import canvas
from django.template.loader import get_template
from django.shortcuts import render
from django.template.context import Context
from django.utils.html import escape
from xhtml2pdf import pisa
import StringIO

def download_report_generation(request):
    answer_list ={}
    answer = ''
    slug = request.GET.get('slug')
    image_url = PMU_URL
    report_id = request.GET.get('report_id')
    project = Project.objects.get_or_none(slug = slug)
    report_obj = ProjectReport.objects.get_or_none(project=project,id=report_id)
    mapping_view = ProjectFunderRelation.objects.get_or_none(project=project)
    report_quarter = QuarterReportSection.objects.filter(project=report_obj)
    parameter_obj = ProjectParameter.objects.filter(active= 2,project=project,parent=None)
    quest_list = Question.objects.filter(active=2,block__block_type = 0)
    for question in quest_list:
        answer_obj = Answer.objects.get_or_none(question =question,
                        content_type = ContentType.objects.get_for_model(report_obj),object_id = report_obj.id)
        if answer_obj and (question.qtype == 'T' or question.qtype == 'APT'):
            answer = str(answer_obj.text) 
        elif answer_obj and (question.qtype == 'F' or question.qtype == 'API'):
            answer = answer_obj.attachment_file.url 
        else:
            answer = ''
        answer_list[str(question.slug)] = answer
    master_pip,master_pin,pin_title_name,pip_title_name,number_json,master_sh = parameter_pie_chart(parameter_obj)
    location = ProjectLocation.objects.filter(object_id=project.id)
    
    template = get_template('report/report-pdf-download.html')
    html = template.render(answer_list)
    result = StringIO.StringIO()
    name = project.name.replace(' ','_')
    file_name = name+'_'+str(report_obj.start_date.strftime('%Y/%m/%d'))+'_To_'+str(report_obj.end_date.strftime('%Y/%m/%d'))+'.pdf'
    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), dest=result )
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename = '+str(file_name)+''
    return response
