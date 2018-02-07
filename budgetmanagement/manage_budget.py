import random
import math
from dateutil import relativedelta
from django.shortcuts import render
from django.db.models import Sum
from datetime import timedelta
from django.template.defaultfilters import slugify
from django.http import HttpResponse,HttpResponseRedirect,JsonResponse
from projectmanagement.models import (Project,MasterCategory,UserProfile)
from .models import (Budget,SuperCategory,ProjectBudgetPeriodConf,BudgetPeriodUnit,
                    Tranche,)
from media.models import (Comment,Attachment)
from django.contrib.contenttypes.models import ContentType
from .forms import(ProjectBudgetForm,)
from datetime import datetime
from menu_decorators import check_loggedin_access

def diff(list1, list2):
    ''' to get the difference of two list '''
    c = set(list1).union(set(list2))
    d = set(list1).intersection(set(list2))
    return list(c - d)

def project_amount_difference(projectobj):
    project_amount = projectobj.project_budget_details()
    planned_amount = project_amount['planned_cost']
    project_amount = int(projectobj.total_budget) if projectobj.total_budget else 0
    final_budget_amount = planned_amount - project_amount if planned_amount > project_amount else 0
    return final_budget_amount

def projectbudgetlist(request):
    '''  for listing the budget '''
    project_slug = request.GET.get("slug")
    budgetlist = Budget.objects.filter(project__slug=project_slug)
    return render(request,"budget/budget_list.html",locals())

def projectbudgetadd(request):
    ''' to create budget (step 1) '''
    key = "budget"
    project_slug = request.GET.get('slug')
    projectobj =  Project.objects.get_or_none(slug=project_slug)
    form = ProjectBudgetForm()
    if request.method == "POST":
        project_slug = request.POST.get('slug')
        projectobj =  Project.objects.get(slug=project_slug)
        form1 = ProjectBudgetForm(request.POST,request.FILES)
        if form1.is_valid():
            form = form1.save(commit=False)
            projectbudgetobj = Budget.objects.create(actual_start_date=request.POST.get("actual_start_date"),end_date=request.POST.get("end_date"),project= projectobj,financial_type=2,start_date = request.POST.get("actual_start_date"), name = projectobj.name )
            projectbudgetobj.save()
            msg = "form is submitted" 
            return HttpResponseRedirect('/manage/project/budget/category/add/?slug='+str(project_slug)+'&budget_id='+str(int(projectbudgetobj.id)))
        else :
            message = "Please fill the form properly"
    return render(request,"budget/budget_create.html",locals())

def projectbudgetcategoryadd(request):
    ''' to create budget category (step 2) '''
    key = "category"
    project_slug = request.GET.get('slug')
    budget_id = request.GET.get('budget_id')
    if request.method == "POST":
        project_slug = request.POST.get('slug')
        budget_id = request.POST.get('budget_id')
        projectobj =  Project.objects.get_or_none(slug=project_slug)
        budgetobj = Budget.objects.get_or_none(id = budget_id )
        supercategoryobj = SuperCategory.objects.create(name = request.POST.get('super-category'),project = projectobj,budget = budgetobj)
        supercategoryobj.slug = slugify(supercategoryobj.name)
        supercategoryobj.save()
        category_names  = [str(k) for k,v in request.POST.items() if k.startswith('category')]
        for i in category_names:
            if request.POST.get(i):
                sub_categoryobj = SuperCategory.objects.create(name = request.POST.get(i),project = projectobj,parent=supercategoryobj,budget = budgetobj)
                sub_categoryobj.slug = slugify(sub_categoryobj.name)
                sub_categoryobj.save()
        return HttpResponseRedirect('/manage/project/budget/lineitem/add/?slug='+str(project_slug)+'&budget_id='+str(int(budgetobj.id)))
    return render(request,"budget/budget_create.html",locals())

def get_budget_logic(budgetobj):
    ''' common functionality to get the start date,end date and no of quarter'''
    sd = budgetobj.actual_start_date
    budget_enddate = budgetobj.end_date
    if sd.day >= 15:
        year = sd.year+1 if sd.month == 12 else sd.year
        month =  1 if sd.month == 12 else sd.month+1
        sd = sd.replace(day=01,month = month,year=year)
    elif sd.day < 15:
        sd = sd.replace(day=01,month = sd.month,year=sd.year)
    ed = budgetobj.end_date
    no_of_quarters = math.ceil(float(((ed.year - sd.year) * 12 + ed.month - sd.month))/3)
    output_data = {'sd':sd,'budget_enddate':budget_enddate,
                   'ed':ed,'no_of_quarters':no_of_quarters}
    return output_data

def get_budget_quarters(budgetobj):
    ''' To get the quarter list i this format 2017-10-01 to 2017-12-31 '''
    data = get_budget_logic(budgetobj)
    sd = data['sd']
    budget_enddate = data['budget_enddate']
    no_of_quarters = data['no_of_quarters']
    ed = data['ed']
    quarter_list = {}
    for i in range(int(no_of_quarters)):
        ed = sd+relativedelta.relativedelta(months=3)
        ed = ed - timedelta(days=1)
        if ed > budget_enddate:
            ed = budget_enddate
        quarter_list.update({i:str(sd)+" to "+str(ed)})
        sd = ed + timedelta(days=1)
    return quarter_list

def get_budget_quarter_names(budgetobj):
    ''' To get the quarter list in jan - feb '''
    data = get_budget_logic(budgetobj)
    ed = data['ed']
    sd = data['sd']
    no_of_quarters = data['no_of_quarters']
    budget_enddate = data['budget_enddate']
    quarter_list = []
    for i in range(int(no_of_quarters)):
        ed = sd+relativedelta.relativedelta(months=3)
        ed = ed - timedelta(days=1)
        if ed > budget_enddate:
            ed = budget_enddate
        quarter_list.append(sd.strftime("%b")+"-"+ed.strftime("%b"))
        sd = ed + timedelta(days=1)
    return quarter_list

def get_lineitem_result(line_itemlist,quarter,request):
    ''' To get the results for each row and for each quarter '''
    result = {}
    for line in line_itemlist:
        line_list = line.split('_')
        if  len(line_list) >= 3:
            if str(quarter) in line.split('_'):
                name = line.split('_')[0]
                result.update({name:request.POST.get(line)})
        else:
            name = line.split('_')[0]
            result.update({name:request.POST.get(line)})
    return result

def projectlineitemadd(request):
    ''' To add budget line items based on quarter and row '''
    project_slug = request.GET.get('slug')
    projectobj =  Project.objects.get_or_none(slug=project_slug)
    project_amount = int(projectobj.total_budget) if projectobj.total_budget else 0
    budget_id = request.GET.get('budget_id')
    budgetobj = Budget.objects.get_or_none(id = budget_id )
    supercategory_list = SuperCategory.objects.filter(active=2,project =projectobj,budget = budgetobj).exclude(parent=None)
    heading_list = MasterCategory.objects.filter(parent__slug="budget-heading",active=2)
    quarter_list = get_budget_quarters(budgetobj)
    if request.method == "POST":
        count = request.POST.get('count')
        project_slug = request.POST.get('slug')
        projectobj =  Project.objects.get_or_none(slug=project_slug)
        budget_id = request.POST.get('budget_id')
        budgetobj = Budget.objects.get_or_none(id = budget_id)
        quarter_list = get_budget_quarters(budgetobj)
        for i in range(int(count)):
            line_itemlist = [str(k) for k,v in request.POST.items() if k.endswith('_'+str(i+1))]
            for quarter,value in quarter_list.items():
                result = get_lineitem_result(line_itemlist,quarter,request)
                if line_itemlist and result["subheading"] :
                    budget_period = value
                    start_date = budget_period.split('to')[0].rstrip()
                    end_date = budget_period.split('to')[1].lstrip()
                    budget_periodobj = ProjectBudgetPeriodConf.objects.create(project = projectobj,budget = budgetobj,start_date=start_date,end_date=end_date,name = projectobj.name,row_order=int(i))
                    budget_dict = {'created_by':UserProfile.objects.get_or_none(user_reference_id = int(request.session.get('user_id'))),
                               'budget_period':budget_periodobj,
                               'category':SuperCategory.objects.get_or_none(id = result['location']),
                               'heading':MasterCategory.objects.get_or_none(id = result['heading']),
                               'subheading':result['subheading'],
                               'unit':result['unit'],
                               'unit_type':result['unit-type'],
                               'rate':result['rate'],
                               'planned_unit_cost':result['planned-cost'],
                               'start_date':start_date,
                               'end_date':end_date,
                               'row_order':int(i),
                               'quarter_order':int(quarter),
                               }
                    budet_lineitem_obj = BudgetPeriodUnit.objects.create(**budget_dict)
        final_budget_amount = project_amount_difference(projectobj)
        return HttpResponseRedirect('/manage/project/budget/view/?slug='+str(project_slug)+"&added=true&final_budget_amount="+str(final_budget_amount))
    return render(request,"budget/budget_lineitem.html",locals())

def projectbudgetdetail(request):
    '''  budget page details based on the project. (old function.)'''
    project_slug = request.GET.get('slug')
    projectobj =  Project.objects.get_or_none(slug=project_slug)
    budget_id = request.GET.get('budget_id')
    budgetobj = Budget.objects.get_or_none(id = budget_id)
    quarter_list = get_budget_quarters(budgetobj)
    budget_period = ProjectBudgetPeriodConf.objects.filter(project = projectobj,budget = budgetobj,active=2).values_list('row_order', flat=True).distinct()
    budget_periodconflist = ProjectBudgetPeriodConf.objects.filter(project = projectobj,budget = budgetobj,active=2).order_by("id")
    span_length = len(budget_periodconflist)
    return render(request,"budget/budget_detail.html",locals())

def get_year_quarterlist(selected_year,budget_id):
    ''' provide the qquarter list based on year choosen in report utlization'''
    budgetobj = Budget.objects.get_or_none(id = budget_id)
    data = get_budget_logic(budgetobj)
    no_of_quarters = data['no_of_quarters']
    ed = data['ed']
    budget_enddate = data['budget_enddate']
    sd = data['sd']
    quarter_list = {}
    for i in range(int(no_of_quarters)):
        ed = sd+relativedelta.relativedelta(months=3)
        ed = ed - timedelta(days=1)
        if ed > budget_enddate:
            ed = budget_enddate
        if str(selected_year) == "Select Year":
            quarter_list.update({i:sd.strftime("%b %Y")+"-"+ed.strftime("%b %Y")})
        if str(sd.year) == str(selected_year) or str(ed.year) == str(selected_year):
            quarter_list.update({i:sd.strftime("%b %Y")+"-"+ed.strftime("%b %Y")})
        sd = ed + timedelta(days=1)
    return quarter_list

def year_quarter_list(request):
    ''' Ajax call function for utilization filter'''
    selected_year = request.GET.get('year')
    budget_id = request.GET.get('budget_id')
    quarter_list = get_year_quarterlist(selected_year,budget_id)
    response = {'quarter_list':quarter_list}
    return JsonResponse(response)

def get_month_quarterlist(selected_year,budget_id):
    ''' provide the qquarter list based on year choosen in report utlization'''
    budgetobj = Budget.objects.get_or_none(id = budget_id)
    ed = budgetobj.end_date
    budget_enddate = budgetobj.end_date
    sd = budgetobj.actual_start_date
    if sd.day >= 15:
        year = sd.year+1 if sd.month == 12 else sd.year
        month =  1 if sd.month == 12 else sd.month+1
        sd = sd.replace(day=01,month = month,year=year)
    elif sd.day < 15:
        sd = sd.replace(day=01,month = sd.month,year=sd.year)

    no_of_quarters = math.ceil(float(((ed.year - sd.year) * 12 + ed.month - sd.month))/1)

    month_list = []
    for i in range(int(no_of_quarters)):
        ed = sd+relativedelta.relativedelta(months=1)
        ed = ed - timedelta(days=1)
        if ed > budget_enddate:
            ed = budget_enddate
        if str(sd.year) == str(selected_year) :
            month_list.append(sd.strftime("%B"))
        sd = ed + timedelta(days=1)
    return month_list

def month_quarter_list(request):
    ''' Ajax call function for month filter'''
    selected_year = request.GET.get('year')
    budget_id = request.GET.get('budget_id')
    month_list = get_month_quarterlist(selected_year,budget_id)
    response = {'month_list':month_list}
    return JsonResponse(response)

def upload_budget_utlized(line_itemlist,i,request,budget_periodobj):
    ''' function to upload the utlized amount based on row and quarter'''
    line_item_updated_values = {}
    for j in line_itemlist:
        item_list = j.split("_")
        if str(i) == item_list[-1]:
            budget_periodobj = BudgetPeriodUnit.objects.get_or_none(id=int(i))
            if str(item_list[0]) == "utilized" :
                line_item_updated_values.update({'utilized_unit_cost':request.POST.getlist(j)[0]})
            elif str(item_list[0]) == "variance": 
                line_item_updated_values.update({item_list[0]:request.POST.getlist(j)[0]})
            elif str(item_list[0]) == "comment":
                text =request.POST.getlist(j)[0]
                commentobj,created = Comment.objects.get_or_create(content_type=ContentType.objects.get_for_model(budget_periodobj),object_id=i)
                commentobj.text = text
                commentobj.save()
            else:
                if request.FILES.get(j):
                    upload = request.FILES.getlist(j)[0]
                    attachobj,created = Attachment.objects.get_or_create(content_type=ContentType.objects.get_for_model(budget_periodobj),object_id=i)
                    attachobj.attachment_file = upload
                    attachobj.save()
    return line_item_updated_values


def budgetutilization(request):
    ''' Report utilization update based on the quarter selected '''
    budget_period = []
    budget_periodconflist = []
    span_length = 0
    quarter_selection_list = []
    quarter_key = request.GET.get('quarter')
    quarter_year = request.GET.get('year')
    project_slug = request.GET.get('slug')
    projectobj =  Project.objects.get_or_none(slug=project_slug)
    budget_id = request.GET.get('budget_id')
    budgetobj = Budget.objects.get_or_none(id = budget_id)
    years_list = []
#    sd = years_list.append(budgetobj.start_date.year)
#    ed = years_list.append(budgetobj.end_date.year)
    sd = budgetobj.start_date.year
    ed = budgetobj.end_date.year
    difference = ed-sd
    years_list = [sd+i for i in range(difference)]
    years_list.append(ed)
    if quarter_key:
        budget_period = ProjectBudgetPeriodConf.objects.filter(project = projectobj,budget = budgetobj,active=2).values_list('row_order', flat=True).distinct()
        budget_periodconflist = ProjectBudgetPeriodConf.objects.filter(project = projectobj,budget = budgetobj,active=2).order_by("id")
        span_length = len(budget_period)
        quarter_selection_list = get_year_quarterlist(quarter_year,budgetobj.id)
        quarter_list = {}
        quarterobj = quarter_list.update(dict([(k,v) for k,v in quarter_selection_list.iteritems() if int(quarter_key) == k]))
    if request.method == "POST":
        count = request.POST.get('count')
        project_slug = request.POST.get('slug')
        projectobj =  Project.objects.get_or_none(slug=project_slug)
        budget_id = request.POST.get('budget_id')
        budgetobj = Budget.objects.get_or_none(id = budget_id)
        quarter_list = get_budget_quarters(budgetobj)
        lineobj_list = filter(None,request.POST.getlist("line_obj"))
        for i in lineobj_list:
            line_itemlist = [str(k) for k,v in request.POST.items() if k.endswith('_'+str(i))]
            #
            # list to get the file attachments 
            line_itemlist.extend( [str(k) for k,v in request.FILES.items() if k.endswith('_'+str(i))])
            
            budget_periodobj = BudgetPeriodUnit.objects.get_or_none(id=int(i))
            line_item_updated_values = upload_budget_utlized(line_itemlist,i,request,budget_periodobj)
            budget_periodobj.__dict__.update(line_item_updated_values)
            budget_periodobj.save()
        from projectmanagement.views import get_project_budget_utilized_amount,auto_update_tranche_amount
        final_budget_utilizedamount = get_project_budget_utilized_amount(projectobj,budgetobj)
        auto_update_tranche_amount(final_budget_utilizedamount,projectobj)
        return HttpResponseRedirect('/manage/project/budget/view/?slug='+str(project_slug))
    return render(request,"budget/budget_utilization.html",locals())

def budget_amount_list(budgetobj,projectobj,quarter_list):
    ''' to get the overall budget amount '''
    quarter_planned_amount = {}
    quarter_utilized_amount = {}
    for i in quarter_list.keys():
        budget_periodlist = ProjectBudgetPeriodConf.objects.filter(project = projectobj,budget = budgetobj,active=2).values_list('id', flat=True)
        budget_period_plannedamount = BudgetPeriodUnit.objects.filter(budget_period__id__in=budget_periodlist,quarter_order=i).values_list('planned_unit_cost', flat=True)
        budget_period_utilizedamount = BudgetPeriodUnit.objects.filter(budget_period__id__in=budget_periodlist,quarter_order=i).values_list('utilized_unit_cost', flat=True)
        budget_period_plannedamount = map(lambda x:x if x else 0,budget_period_plannedamount)
        final_budget_period_plannedamount = sum(map(float,budget_period_plannedamount))
        budget_period_utilizedamount = map(lambda x:x if x else 0,budget_period_utilizedamount)
        final_budget_period_utilizedamount = sum(map(float,budget_period_utilizedamount))
        quarter_planned_amount.update({i:final_budget_period_plannedamount})
        quarter_utilized_amount.update({i:final_budget_period_utilizedamount})
    budget_period_plannedamount = quarter_planned_amount.values()
    budget_period_utilizedamount = quarter_utilized_amount.values()
    return map(int,budget_period_plannedamount),map(float,budget_period_utilizedamount)

def tanchesamountlist(tranche_list):
     ''' to get the tranches detail amount'''
     planned_amount = tranche_list.aggregate(Sum('planned_amount')).values()[0]
     actual_disbursed_amount = tranche_list.aggregate(Sum('actual_disbursed_amount')).values()[0]
     recommended_amount = tranche_list.aggregate(Sum('recommended_amount')).values()[0]
     utilized_amount = tranche_list.aggregate(Sum('utilized_amount')).values()[0]
     tranche_amount = {'planned_amount':planned_amount,
                       'actual_disbursed_amount':actual_disbursed_amount,
                       'recommended_amount':recommended_amount,
                       'utilized_amount': utilized_amount
                       }
     return tranche_amount

def budget_supercategory_value(projectobj,budgetobj):
    colors= [
    '#5485BC', '#AA8C30', '#5C9384', '#981A37', '#FCB319',     '#86A033', '#614931', '#00526F', '#594266', '#cb6828', '#aaaaab', '#a89375'
    ]
    project_category_list = SuperCategory.objects.filter(project = projectobj,active=2).exclude(parent=None)
    final_project_category_list = []
    for i in project_category_list:
        total_amount_list = BudgetPeriodUnit.objects.filter(budget_period__budget = budgetobj,budget_period__project=projectobj,category=i,active=2).values_list('planned_unit_cost',flat=True)
        total_amount_list = map(lambda x:x if x else 0,total_amount_list)
        total_amount_number = map(float,total_amount_list)
        total_amount = sum(total_amount_number)
        final_project_category_list.append({'name':i.name,'y':int(total_amount),'color':random.choice(colors)})
    return final_project_category_list

@check_loggedin_access
def budgetview(request):
    '''  Redirecting to the budget summary page based on the budget object creation status '''
    project_slug = request.GET.get('slug')
    projectobj =  Project.objects.get_or_none(slug=project_slug)
    budgetobj = Budget.objects.latest_one(project = projectobj,active=2)
    super_categorylist = SuperCategory.objects.filter(budget = budgetobj,active=2).exclude(parent=None)
    user_id = request.session.get('user_id')
    user = UserProfile.objects.get_or_none(user_reference_id = user_id)
    from taskmanagement.views import get_assigned_users
    status = get_assigned_users(user,projectobj)
    key = request.GET.get('key')
    if budgetobj:
        sd = budgetobj.start_date.year
        ed = budgetobj.end_date.year
        difference = ed-sd
        years_list = [sd+i for i in range(difference)]
        years_list.append(ed)
        quarter_list = get_budget_quarters(budgetobj)
        filter_quarter_list = quarter_list
        quarter_names = get_budget_quarter_names(budgetobj)
        budget_period = ProjectBudgetPeriodConf.objects.filter(project = projectobj,budget = budgetobj,active=2).values_list('row_order', flat=True).distinct()
        budget_periodconflist = ProjectBudgetPeriodConf.objects.filter(project = projectobj,budget = budgetobj,active=2).order_by("id")
        span_length = len(budget_period)
        budget_planned_amount,budget_utilized_amount = budget_amount_list(budgetobj,projectobj,quarter_list)
        tranche_list = Tranche.objects.filter(project = projectobj,active=2).order_by("disbursed_date")
        tranche_amount = tanchesamountlist(tranche_list)
        planned_amount = tranche_amount['planned_amount']
        actual_disbursed_amount = tranche_amount['actual_disbursed_amount']
        recommended_amount = tranche_amount['recommended_amount']
        utilized_amount = tranche_amount['utilized_amount']
        final_project_category_list = budget_supercategory_value(projectobj,budgetobj)
        if not super_categorylist:
            return HttpResponseRedirect('/manage/project/budget/category/add/?slug='+str(project_slug)+'&budget_id='+str(int(budgetobj.id)))
        if not budget_period:
            return HttpResponseRedirect('/manage/project/budget/lineitem/add/?slug='+str(project_slug)+'&budget_id='+str(int(budgetobj.id)))
        category_names = SuperCategory.objects.filter(project=projectobj).exclude(parent=None)
    return render(request,"budget/budget.html",locals())


def inactivatingthelineitems(projectobj,lineobj_list):
    '''
        inactivating the removed line items
    '''
    budget_lineitem_ids = BudgetPeriodUnit.objects.filter(budget_period__project = projectobj,active=2).values_list('id',flat=True)
    budget_lineitem_ids = map(int,budget_lineitem_ids)
    lineobj_list = map(int,lineobj_list)
    final_list = diff(lineobj_list,budget_lineitem_ids)
    if final_list:
        for i in final_list:
            periodobj = BudgetPeriodUnit.objects.get_or_none(id=i)
            if periodobj:
                periodobj.active = 0
                periodobj.budget_period.active = 0
                periodobj.save()
                periodobj.budget_period.save()
    ''' inactivating line items ends '''
    return final_list

def get_budget_edit_result(line_itemlist,quarter,request):
    '''  Function to prepare the result list'''
    result = {}
    budgetperiodid = None
    for line in line_itemlist:
        line_list = line.split('_')
        if  len(line_list) >= 3:
            if str(quarter) == str(line.split('_')[1]) :
                name = line.split('_')[0]
                budgetperiodid = line.split('_')[2]
                result.update({name:request.POST.get(line)})
        else:
            name = line.split('_')[0]
            result.update({name:request.POST.get(line)})
    return result,budgetperiodid

def budget_lineitem_update(budget_parameters):
    ''' function to update the line items '''
    data_item  = budget_parameters
    budgetperiodid = data_item['budgetperiodid']
    budget_dict = data_item['budget_dict']
    result = data_item['result']
    if budgetperiodid:
        budget_lineitem_obj = BudgetPeriodUnit.objects.get_or_none(id=int(budgetperiodid))
        budget_lineitem_obj.__dict__.update(budget_dict)
        budget_lineitem_obj.save()
        utilized_amount = budget_lineitem_obj.utilized_unit_cost if budget_lineitem_obj.utilized_unit_cost else 0
        planned_cost = float(result['planned-cost']) if result['planned-cost'] else 0 
        budget_lineitem_obj.variance = planned_cost - int(utilized_amount)
        budget_lineitem_obj.save()
    else:
        start_date = data_item['start_date']
        end_date = data_item['end_date']
        j = data_item['j']
        budgetobj = data_item['budgetobj']
        projectobj = data_item['projectobj']
        request = data_item['request']
        quarter = data_item['quarter']
        budget_periodobj = ProjectBudgetPeriodConf.objects.create(project = projectobj,budget = budgetobj,start_date=start_date,end_date=end_date,name = projectobj.name,row_order=int(j))
        budget_lineitem_obj = BudgetPeriodUnit.objects.create(**budget_dict)
        budget_extra_values = {
                   'created_by_id':UserProfile.objects.get_or_none(user_reference_id = int(request.session.get('user_id'))).id,
                   'row_order':int(j),
                   'quarter_order':int(quarter),
                   'budget_period_id':budget_periodobj.id,
                   'variance':float(budget_lineitem_obj.planned_unit_cost) if budget_lineitem_obj.planned_unit_cost else 0
                   }
        budget_lineitem_obj.__dict__.update(budget_extra_values)
        budget_lineitem_obj.save()
    return budget_lineitem_obj

def update_budget_lineitemedit(line_itemlist,quarter_list,request,j,budgetobj,projectobj):
    for quarter,value in quarter_list.items():
        start_date = value.split('to')[0].rstrip()
        end_date = value.split('to')[1].lstrip()
        result,budgetperiodid = get_budget_edit_result(line_itemlist,quarter,request)
        if result["subheading"]:
            budget_dict = {
                       'category_id':SuperCategory.objects.get_or_none(id = result['location']).id,
                       'heading_id':MasterCategory.objects.get_or_none(id = result['heading']).id,
                       'subheading':result['subheading'],
                       'unit':result['unit'],
                       'unit_type':result['unit-type'],
                       'rate':result['rate'],
                       'planned_unit_cost':result['planned-cost'],
                       'start_date':start_date,
                       'end_date':end_date,
                       'row_order':int(j),
                       'quarter_order':int(quarter),
                       }
            budget_parameters = {'budgetperiodid':budgetperiodid,
                                'budget_dict':budget_dict,
                                'result':result,'start_date':start_date,
                                'end_date':end_date,'j':j,'budgetobj':budgetobj,
                                'projectobj':projectobj,'request':request,
                                'quarter':quarter}
            budget_saving = budget_lineitem_update(budget_parameters)
    return line_itemlist


def budgetlineitemedit(request):
    '''  Function to edit the budget line item'''
    project_slug = request.GET.get('slug')
    projectobj =  Project.objects.get_or_none(slug=project_slug)
    budget_id = request.GET.get('budget_id')
    budgetobj = Budget.objects.get_or_none(id = budget_id )
    project_amount = int(projectobj.total_budget) if projectobj.total_budget else 0
    supercategory_list = SuperCategory.objects.filter(active=2,project =projectobj,budget = budgetobj).exclude(parent=None)
    heading_list = MasterCategory.objects.filter(parent__slug="budget-heading",active=2)
    quarter_list = get_budget_quarters(budgetobj)
    budget_period = ProjectBudgetPeriodConf.objects.filter(project = projectobj,budget = budgetobj,active=2).values_list('row_order', flat=True).distinct()
    budget_periodconflist = ProjectBudgetPeriodConf.objects.filter(project = projectobj,budget = budgetobj,active=2).order_by("id")
    span_length = len(budget_period)
    if request.method == "POST":
        count = request.POST.get('count')
        project_slug = request.POST.get('slug')
        projectobj =  Project.objects.get_or_none(slug=project_slug)
        budget_id = request.POST.get('budget_id')
        budgetobj = Budget.objects.get_or_none(id = budget_id)
        quarter_list = get_budget_quarters(budgetobj)
        lineobj_list = filter(None,request.POST.getlist("line_obj"))
        final_result = inactivatingthelineitems(projectobj,lineobj_list)
        for j in range((int(count)+1)):
            line_itemlist = [str(k) for k,v in request.POST.items() if k.endswith('_'+str(j))]
            if line_itemlist:
#                splitted the code to reduce the sonar issues
                budget_saving = update_budget_lineitemedit(line_itemlist,quarter_list,request,j,budgetobj,projectobj)

        final_budget_amount = project_amount_difference(projectobj)
        return HttpResponseRedirect('/manage/project/budget/view/?slug='+str(project_slug)+"&edit=true&final_budget_amount="+str(final_budget_amount))
    return render(request,"budget/edit_budgetlineitem.html",locals())
    
def category_listing(request):
    # this is to list the categories which are added 
    budget_id = request.GET.get('budget_id')
    project_slug = request.GET.get('slug')
    listing = SuperCategory.objects.filter(budget__id=budget_id,project__slug = project_slug).exclude(parent=None)
    return render(request,"budget/category_listing.html",locals())

def category_add(request):
    # this is to add super categories for the project
    budget_id = request.GET.get('budget_id')
    project_slug = request.GET.get('slug')
    if request.method == 'POST':
        budget_id = request.POST.get('budget_id')
        project_slug = request.POST.get('slug')
        project_obj = Project.objects.get_or_none(slug=project_slug)
        budget_obj = Budget.objects.get_or_none(id=int(budget_id))
        super_parent = SuperCategory.objects.filter(budget=budget_obj,project=project_obj)[1].parent
        category_names  = [str(k) for k,v in request.POST.items() if k.startswith('category')]
        for i in category_names:
            if request.POST.get(i):
                super_obj = SuperCategory.objects.create(name = request.POST.get(i),project = project_obj,parent=super_parent,budget = budget_obj)
                super_obj.slug = slugify(super_obj.name)
                super_obj.save()
        return HttpResponseRedirect('/manage/project/budget/view/?slug='+str(project_slug)+'&key=budget')
    return render(request,"budget/category_edit.html",locals())

def delete_category(request):
    # this is to delete a category
    budget_id=request.GET.get('budget_id')
    project_slug = request.GET.get('slug')
    catgry_id = request.GET.get('cat_id')
    catgery_del = SuperCategory.objects.get(id=catgry_id).delete()
    return HttpResponseRedirect('/manage/project/budget/category/listing/?budget_id='+str(budget_id)+'&slug='+project_slug)
