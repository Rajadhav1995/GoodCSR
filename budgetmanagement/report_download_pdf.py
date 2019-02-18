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
from menu_decorators import check_loggedin_access
from wkhtmltopdf.views import PDFTemplateView, PDFTemplateResponse

from django.template import Context, Template, RequestContext
# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.    
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

from django.template import Context
from django.template.loader import render_to_string
class MyPDF(PDFTemplateView):
    def get_context_data(self, **kwargs):
        context = super(MyPDF, self).get_context_data(**kwargs)
        return context
@check_loggedin_access
def pdfconverter(request):
    # this function we are using to generate pdf 
    # for project report 
    slug = request.GET.get('slug')
    report_id = request.GET.get('report_id')
    project = Project.objects.get_or_none(slug = slug)
    key = int(request.GET.get('key'))
    # 1 for old pdf and 2 for new pdf
    report_obj = ProjectReport.objects.get(id=report_id)
    options = {
    '--load-error-handling': 'ignore',
    '--header-html': PMU_URL+'/report/pdf/view/header/?report_id='+report_id,
    '--footer-html':  PMU_URL+'/report/pdf/view/footer/?report_id='+report_id,
    '--header-spacing': '20.10',
    '--encoding': "utf-8",
    '--footer-right': '[page]',
    }
    import datetime
    dd = datetime.datetime.today()
    file_name = project.slug +'_' +dd.strftime('%d_%m_%Y_%s') +".pdf"
    file_path = BASE_DIR+'/'+file_name
    #try:
        # pdfkit.from_url(PMU_URL+'/report/detail/?slug='+str(slug)+'&report_id='+str(report_id)+'&key='+'2', BASE_DIR +'/static/pdf-reports/'+ file_name,options=options)
    template = 'report/report-template_pdf_copy.html'
    from .remove_pdf_view import *
    import requests
    import ipdb;ipdb.set_trace()
    #locals_list = requests.get(PMU_URL+'/report/display/blocks/?slug='+str(slug)+'&report_id='+str(report_id)+'&key='+'2')
    
    project_slug = request.GET.get('slug')
    report_id = request.GET.get('report_id')
    survey = Survey.objects.get(id=1)
    image_url = PMU_URL
    block1 = Block.objects.get_or_none(survey=survey,name__iexact = 'Cover Page',block_type=0)
    block2 = Block.objects.get_or_none(survey=survey,name__iexact = 'Project Summary Sheet',block_type=0)
    project_report = ProjectReport.objects.get_or_none(id=report_id)
    project = Project.objects.get_or_none(slug=project_slug)
    mapping_view = ProjectFunderRelation.objects.get_or_none(project=project)
    
    locals_list={'block1':block1,'block2':block2,'project_report':project_report,'mapping_view':mapping_view}
    data = get_pdf_view_download(slug,report_id,report_obj.report_type,2,locals_list)
    
    
    #context = Context(data)
    #html=template.render(context)
    #message=render_to_string(BASE_DIR +'/static/pdf-reports/'+ file_name)
    #pdfkit.from_url(PMU_URL+'/report/remove/detail/?slug='+str(slug)+'&report_id='+str(report_id)+'&key='+'2'+'&report_type='+str(report_obj.report_type), BASE_DIR +'/static/pdf-reports/'+ file_name,options=options)
    #except:
     #   return HttpResponseRedirect(PMU_URL+'/static/pdf-reports/'+ file_name)
    fs = FileSystemStorage()
    # after generating pdf file we are saving it in
    # /static/pdf-reports/ directory and after that
    # 
    #data = {'report_id':str(report_id),'slug':str(slug)}
    #message=render_to_string(template,data)
    return PDFTemplateResponse(
                            request=request,
                            template=template,
                            filename=file_path,
                            context=data
                            )

            # write the rendered content to a file
    #with open("file.pdf", "wb") as f:
        #f.write(response.rendered_content)
    
    
    #return MyPDF.as_view(template_name=message, filename='my_pdf.pdf')
    #with open(file_path,'w+') as pdfss:
        #message=render_to_string(template,data)
        #template= get_template(template).render(data)
        #pdfkit.from_string(message,file_path)
        #response = HttpResponse(pdfss, content_type='application/pdf')
        #response['Content-Disposition'] = 'attachment; filename='+file_name
        #return response
    #return response

def pdf_header(request):
    # this function is to show header
    # in pdf project report
    image_url = PMU_URL
    report_id = int(request.GET.get('report_id'))
    impl_part_ques = Question.objects.get_or_none(slug='logos')
    funder_ques = Question.objects.get_or_none(slug='client_logo')
    impl_ans = Answer.objects.get_or_none(question=impl_part_ques,object_id=report_id)
    funder_ans = Answer.objects.get_or_none(question=funder_ques,object_id=report_id)
    report = ProjectReport.objects.get(id=report_id)
    question = Question.objects.get_or_none(slug='report_name')
    block_questions = Question.objects.filter(block__slug='cover-page',parent=None)
    ans = Answer.objects.get_or_none(question=question,object_id=report_id)
    if ans:
        report_name = ans.text
    return render(request,'report/header.html',locals())

def pdf_footer(request):
    # this function is to show footer 
    # in pdf project report
    image_url = PMU_URL
    report_id = int(request.GET.get('report_id'))
    report = ProjectReport.objects.get(id=report_id)
    return render(request,'report/footer.html',locals())



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
