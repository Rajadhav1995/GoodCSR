from budgetmanagement.report_generate import *

from budgetmanagement.common_method import key_parameter_chart
from projectmanagement.views import parameter_pie_chart
# this imports for the pdf download where the packages to be installed are 
import csv
from reportlab.pdfgen import canvas
from django.template.loader import get_template
from django.shortcuts import render
from django.template.context import Context
from django.utils.html import escape
from xhtml2pdf import pisa
import StringIO
import pdfkit
from pmu.settings import BASE_DIR,PMU_URL

def download_report_generation(request):
#to download the pdf of the report generated and fetching the details of what to be dislayed in the pdf
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
    cover_image = Attachment.objects.get_or_none(description__iexact = "cover image",attachment_type = 1,
            content_type = ContentType.objects.get_for_model(report_obj),
            object_id = report_obj.id)
    details = {'report_type':report_obj.get_report_type_display(),
        'report_duration':report_obj.start_date.strftime('%Y-%m-%d')+' TO '+report_obj.end_date.strftime('%Y-%m-%d'),
        'prepared_by':report_obj.created_by.name,'client_name':mapping_view.funder.organization,
        'report_name':report_obj.name if report_obj.name else '',
        'cover_image': cover_image.attachment_file.url if cover_image else '',
        'project_title':project.name,'project_budget':project.total_budget,
        'donor':mapping_view.funder.organization,
        'implement_ngo':mapping_view.implementation_partner.organization,
        'no_of_beneficiaries':project.no_of_beneficiaries,'project_duration':project.start_date.strftime('%Y-%m-%d')+' TO '+project.end_date.strftime('%Y-%m-%d'),
        'location':project.get_locations()}
        
    quest_list = Question.objects.filter(active=2,block__block_type = 0).exclude(qtype='OT')
    for question in quest_list:
        answer_obj = Answer.objects.get_or_none(question =question,
                        content_type = ContentType.objects.get_for_model(report_obj),object_id = report_obj.id)
        if answer_obj and (question.qtype == 'T' or question.qtype == 'APT'):
            answer = str(answer_obj.text) 
        elif answer_obj and (question.qtype == 'F' or question.qtype == 'API') and answer_obj.attachment_file:
            answer = answer_obj.attachment_file.url 
        else:
            try:
                answer = details[str(question.slug)]
            except:
                answer = ''
        answer_list[str(question.slug)] = answer
    master_pip,master_pin,pin_title_name,pip_title_name,number_json,master_sh = parameter_pie_chart(parameter_obj)
    location = ProjectLocation.objects.filter(object_id=project.id)
    # this is to make html to pdf 
    
    template = get_template('report/report-pdf-download.html')
    html = template.render(answer_list)
    result = StringIO.StringIO()
    name = project.name.replace(' ','_')
    file_name = name+'_'+str(report_obj.start_date.strftime('%Y/%m/%d'))+'_To_'+str(report_obj.end_date.strftime('%Y/%m/%d'))+'.pdf'
    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), dest=result,  link_callback=fetch_resources )
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename = '+str(file_name)+''
    return response
    
def fetch_resources(uri, rel):
    import os
    import cgi
    from django.conf import settings
    path = PMU_URL + os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    return path

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseNotFound
from io import BytesIO
from reportlab.pdfgen import canvas
import re
import base64

def pdf_view(request):
    fs = FileSystemStorage()
    filename = 'testp.pdf'
    if fs.exists(filename):
        with fs.open(filename) as pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="testp.pdf"'
            return response
    else:
        return HttpResponseNotFound('The requested pdf was not found in our server.')


def pdfconverter(request):
    slug = request.GET.get('slug')
    report_id = request.GET.get('report_id')
    project = Project.objects.get_or_none(slug = slug)
    
    options = {
    '--load-error-handling': 'ignore',
    '--header-html': PMU_URL+'/report/pdf/view/header/?report_id='+report_id,
    '--footer-html':  PMU_URL+'/report/pdf/view/footer/?report_id='+report_id,
    '--margin-bottom': '15.50',
    '--encoding': "utf-8",
    '--footer-right': '[page]',
    }
    import datetime
    dd = datetime.datetime.today()
    file_name = project.slug +'_' +dd.strftime('%d_%m_%Y_%s') +".pdf"
    pdfkit.from_url(PMU_URL+'/report/detail/?slug='+str(slug)+'&report_id='+str(report_id)+'&key='+'2', BASE_DIR +'/static/pdf-reports/'+ file_name)
    fs = FileSystemStorage()
    with fs.open(BASE_DIR +'/static/pdf-reports/'+ file_name) as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename='+file_name
        return response

    return response

def pdf_header_data(report):
    report_obj=ProjectReport.objects.get(id=report)
    question = Question.objects.get(slug='report_name')
    ans = Answer.objects.get(question=question,object_id=t.id)
    return ans.text,


def pdf_header(request):
    image_url = PMU_URL
    report_id = int(request.GET.get('report_id'))
    impl_part_ques = Question.objects.get_or_none(slug='logos')
    funder_ques = Question.objects.get_or_none(slug='client_logo')
    impl_ans = Answer.objects.get_or_none(question=impl_part_ques,object_id=report_id)
    funder_ans = Answer.objects.get_or_none(question=funder_ques,object_id=report_id)
    report = ProjectReport.objects.get(id=report_id)
    question = Question.objects.get_or_none(slug='report_name')
    ans = Answer.objects.get_or_none(question=question,object_id=report_id)
    report_name = ans.text
    # report_name = pdf_header_data(report)
    return render(request,'report/header.html',locals())

def pdf_footer(request):
    image_url = PMU_URL
    report_id = int(request.GET.get('report_id'))
    report = ProjectReport.objects.get(id=report_id)
    return render(request,'report/footer.html',locals())