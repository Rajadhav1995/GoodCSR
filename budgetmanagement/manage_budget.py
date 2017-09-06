import random
import math
from dateutil import relativedelta
from django.shortcuts import render
from django.db.models import Sum
from datetime import timedelta
from django.template.defaultfilters import slugify
from django.http import HttpResponse,HttpResponseRedirect
from projectmanagement.models import (Project,MasterCategory,UserProfile)
from .models import (Budget,SuperCategory,ProjectBudgetPeriodConf,BudgetPeriodUnit,
                    Tranche,)
from media.models import (Comment,)
from django.contrib.contenttypes.models import ContentType
from .forms import(ProjectBudgetForm,)
from datetime import datetime

def projectbudgetlist(request):
    project_slug = request.GET.get("slug")
    budgetlist = Budget.objects.filter(project__slug=project_slug)
    return render(request,"budget/budget_list.html",locals())

def projectbudgetadd(request):
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

def get_budget_quarters(budgetobj):
    sd = budgetobj.actual_start_date
    budget_enddate = budgetobj.end_date
    if sd.day > 15:
        year = sd.year+1 if sd.month == 12 else sd.year
        sd = sd.replace(day=01,month = sd.month+1,year=year)
    ed = budgetobj.end_date
    no_of_quarters = math.ceil(float(((ed.year - sd.year) * 12 + ed.month - sd.month))/3)
    quarter_list = {}
    for i in range(int(no_of_quarters)):
        ed = sd+relativedelta.relativedelta(months=3)
        if ed > budget_enddate:
            ed = budget_enddate
        quarter_list.update({i:str(sd)+" to "+str(ed)})
        sd = ed
    return quarter_list

def get_budget_quarter_names(budgetobj):
    sd = budgetobj.actual_start_date
    budget_enddate = budgetobj.end_date
    if sd.day > 15:
        year = sd.year+1 if sd.month == 12 else sd.year
        sd = sd.replace(day=01,month = sd.month+1,year=year)
    ed = budgetobj.end_date
    no_of_quarters = math.ceil(float(((ed.year - sd.year) * 12 + ed.month - sd.month))/3)
    quarter_list = []
    for i in range(int(no_of_quarters)):
        ed = sd+relativedelta.relativedelta(months=3)
        if ed > budget_enddate:
            ed = budget_enddate
        quarter_list.append(sd.strftime("%b")+"-"+ed.strftime("%b"))
        sd = ed
    return quarter_list

def projectlineitemadd(request):
    project_slug = request.GET.get('slug')
    projectobj =  Project.objects.get_or_none(slug=project_slug)
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
                if result["subheading"]:
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
#                               'utilized_unit_cost':result['utilized-cost'],
                               'start_date':start_date,
                               'end_date':end_date,
                               'row_order':int(i),
                               'quarter_order':int(quarter),
                               }
                    budet_lineitem_obj = BudgetPeriodUnit.objects.create(**budget_dict)
        return HttpResponseRedirect('/manage/project/budget/view/?slug='+str(project_slug))
    return render(request,"budget/budget_lineitem.html",locals())

def projectbudgetdetail(request):
    project_slug = request.GET.get('slug')
    projectobj =  Project.objects.get_or_none(slug=project_slug)
    budget_id = request.GET.get('budget_id')
    budgetobj = Budget.objects.get_or_none(id = budget_id)
    quarter_list = get_budget_quarters(budgetobj)
    budget_period = ProjectBudgetPeriodConf.objects.filter(project = projectobj,budget = budgetobj).values_list('row_order', flat=True).distinct()
    budget_periodconflist = ProjectBudgetPeriodConf.objects.filter(project = projectobj,budget = budgetobj).order_by("id")
    span_length = len(budget_periodconflist)
    return render(request,"budget/budget_detail.html",locals())

def budgetutilization(request):
    quarter_key = request.GET.get('quarter')
    project_slug = request.GET.get('slug')
    projectobj =  Project.objects.get_or_none(slug=project_slug)
    budget_id = request.GET.get('budget_id')
    budgetobj = Budget.objects.get_or_none(id = budget_id)
    quarter_selection_list = get_budget_quarters(budgetobj)
    if quarter_key:
        budget_period = ProjectBudgetPeriodConf.objects.filter(project = projectobj,budget = budgetobj).values_list('row_order', flat=True).distinct()
        budget_periodconflist = ProjectBudgetPeriodConf.objects.filter(project = projectobj,budget = budgetobj).order_by("id")
        span_length = len(budget_period)
        quarter_selection_list = get_budget_quarters(budgetobj)
#        import ipdb.ipdb.set_trace();
        quarter_list = [(k,v) for k,v in quarter_selection_list.iteritems() if int(quarter_key) in k]
    else:
        budget_period = []
        budget_periodconflist = []
        span_length = 0
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
            line_item_updated_values = {}
            for j in line_itemlist:
                item_list = j.split("_")
                if str(i) == item_list[-1]:
                    budget_periodobj = BudgetPeriodUnit.objects.get_or_none(id=int(i))
                    if str(item_list[0]) == "utilized" :
                        line_item_updated_values.update({'utilized_unit_cost':request.POST.getlist(j)[0]})
                    elif str(item_list[0]) == "variance": 
                        line_item_updated_values.update({item_list[0]:request.POST.getlist(j)[0]})
                    else:
                        text =request.POST.getlist(j)[0]
                        commentobj,created = Comment.objects.get_or_create(content_type=ContentType.objects.get_for_model(budget_periodobj),object_id=i)
                        commentobj.text = text
                        commentobj.save()
            budget_periodobj.__dict__.update(line_item_updated_values)
            budget_periodobj.save()
        return HttpResponseRedirect('/manage/project/budget/view/?slug='+str(project_slug))
    return render(request,"budget/budget_utilization.html",locals())

def budget_amount_list(budgetobj,projectobj,quarter_list):
    quarter_planned_amount = {}
    quarter_utilized_amount = {}
    for i in quarter_list.keys():
        budget_periodlist = ProjectBudgetPeriodConf.objects.filter(project = projectobj,budget = budgetobj).values_list('id', flat=True)
        budget_period_plannedamount = BudgetPeriodUnit.objects.filter(budget_period__id__in=budget_periodlist,quarter_order=i).values_list('planned_unit_cost', flat=True)
        budget_period_utilizedamount = BudgetPeriodUnit.objects.filter(budget_period__id__in=budget_periodlist,quarter_order=i).values_list('utilized_unit_cost', flat=True)
        budget_period_plannedamount = map(lambda x:x if x else 0,budget_period_plannedamount)
        final_budget_period_plannedamount = sum(map(int,budget_period_plannedamount))
        budget_period_utilizedamount = map(lambda x:x if x else 0,budget_period_utilizedamount)
        final_budget_period_utilizedamount = sum(map(int,budget_period_utilizedamount))
        quarter_planned_amount.update({i:final_budget_period_plannedamount})
        quarter_utilized_amount.update({i:final_budget_period_utilizedamount})
    budget_period_plannedamount = quarter_planned_amount.values()
    budget_period_utilizedamount = quarter_utilized_amount.values()
    return map(int,budget_period_plannedamount),map(int,budget_period_utilizedamount)

def tanchesamountlist(tranche_list):
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
#    budget_categorylist = BudgetPeriodUnit.objects.filter(budget_period__budget = budgetobj).values_list('category_id', flat=True).distinct()
    colors= [
    '#5485BC', '#AA8C30', '#5C9384', '#981A37', '#FCB319',     '#86A033', '#614931', '#00526F', '#594266', '#cb6828', '#aaaaab', '#a89375'
    ]
    project_category_list = SuperCategory.objects.filter(project = projectobj,active=2).exclude(parent=None)
    final_project_category_list = []
    for i in project_category_list:
        total_amount_list = BudgetPeriodUnit.objects.filter(budget_period__budget = budgetobj,budget_period__project=projectobj,category=i).values_list('planned_unit_cost',flat=True)
        total_amount_list = map(lambda x:x if x else 0,total_amount_list)
        total_amount_number = map(int,total_amount_list)
        total_amount = sum(total_amount_number)
        final_project_category_list.append({'name':i.name,'y':int(total_amount),'color':random.choice(colors)})
    return final_project_category_list

def budgetview(request):

    project_slug = request.GET.get('slug')
    projectobj =  Project.objects.get_or_none(slug=project_slug)
    budgetobj = Budget.objects.latest_one(project = projectobj,active=2)
    if budgetobj:
        quarter_list = get_budget_quarters(budgetobj)
        quarter_names = get_budget_quarter_names(budgetobj)
        budget_period = ProjectBudgetPeriodConf.objects.filter(project = projectobj,budget = budgetobj).values_list('row_order', flat=True).distinct()
        budget_periodconflist = ProjectBudgetPeriodConf.objects.filter(project = projectobj,budget = budgetobj).order_by("id")
        span_length = len(budget_period)
        budget_planned_amount,budget_utilized_amount = budget_amount_list(budgetobj,projectobj,quarter_list)
        tranche_list = Tranche.objects.filter(project = projectobj)
        tranche_amount = tanchesamountlist(tranche_list)
        planned_amount = tranche_amount['planned_amount']
        actual_disbursed_amount = tranche_amount['actual_disbursed_amount']
        recommended_amount = tranche_amount['recommended_amount']
        utilized_amount = tranche_amount['utilized_amount']
        
        final_project_category_list = budget_supercategory_value(projectobj,budgetobj)
    return render(request,"budget/budget.html",locals())
