from budgetmanagement.report_generate import *

def remove_functionality_pdf_view(request):
    slug = request.GET.get('slug')
    report_id = request.GET.get('report_id')
    pdf_key = int(request.GET.get('key'))
    report_type = int(request.GET.get('report_type'))
    image = PMU_URL
    #to display the cover page and summary page sections calling the functions by passing request #STARTS)
    locals_list = display_blocks(request)
    # end of the display cover page and summary #ENDS
    projectobj = Project.objects.get_or_none(slug=slug)
    budgetobj = Budget.objects.latest_one(project = projectobj,active=2)
    projectreportobj = ProjectReport.objects.get_or_none(id=request.GET.get('report_id'))
    quest_list = Question.objects.filter(active=2,block__block_type = 0)
    answer_list = report_question_list(quest_list,projectreportobj,projectobj)
    if report_type == 1:
        previousquarter_list,currentquarter_list,futurequarter_list = {},{},{}
        if projectreportobj:
            previousquarter_list,currentquarter_list,futurequarter_list = get_quarters(projectreportobj)
        #    to display the index page 
    elif report_type == 2:
        # here logic for monthly report
        from budgetmanagement.common_method import get_monthly_logic
        previousquarter_list,currentquarter_list,futurequarter_list = get_monthly_logic(projectreportobj,budgetobj)
    previous_questionlist = Question.objects.filter(active = 2,block__slug="previous-quarter-update",parent=None).order_by("order")
    current_questionlist = Question.objects.filter(active = 2,block__slug="current-quarter-update",parent=None).order_by("order")
    next_questionlist = Question.objects.filter(active = 2,block__slug="next-quarter-update",parent=None).order_by("order")
    tranche_list = Tranche.objects.filter(project = projectobj,active=2)
    tranche_amount = tanchesamountlist(tranche_list)
    planned_amount = tranche_amount['planned_amount']
    actual_disbursed_amount = tranche_amount['actual_disbursed_amount']
    recommended_amount = tranche_amount['recommended_amount']
    utilized_amount = tranche_amount['utilized_amount']
    contents,quarters,number_dict = get_index_contents(slug,report_id)
    for key, value in sorted(contents.iteritems(), key=lambda (k,v): (v,k)):
        contents[key]=value
    if pdf_key == 1:
        return render(request,'report/remove-pdfview.html',locals())
    else:
        return render(request,'report/report-template_pdf_copy.html',locals())
# 
