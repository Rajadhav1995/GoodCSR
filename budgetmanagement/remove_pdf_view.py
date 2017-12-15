from budgetmanagement.report_generate import *

def remove_functionality_pdf_view(request):
    slug = request.GET.get('slug')
    report_id = request.GET.get('report_id')
    key = request.GET.get('key')
    #to display the cover page and summary page sections calling the functions by passing request #STARTS)
    locals_list = display_blocks(request)
    # end of the display cover page and summary #ENDS
    projectobj = Project.objects.get_or_none(slug=slug)
    budgetobj = Budget.objects.latest_one(project = projectobj,active=2)
    projectreportobj = ProjectReport.objects.get_or_none(id=request.GET.get('report_id'))
    quest_list = Question.objects.filter(active=2,block__block_type = 0)
    answer_list = report_question_list(quest_list,projectreportobj,projectobj)
#    to display the index page 
    contents,quarters,number_dict = get_index_contents(slug,report_id)
    for key, value in sorted(contents.iteritems(), key=lambda (k,v): (v,k)):
        contents[key]=value
    return render(request,'report/remove-pdfview.html',locals())
