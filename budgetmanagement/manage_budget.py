from django.shortcuts import render
from datetime import timedelta
from django.template.defaultfilters import slugify
from django.http import HttpResponse,HttpResponseRedirect
from projectmanagement.models import (Project,MasterCategory,UserProfile)
from .models import (Budget,SuperCategory,ProjectBudgetPeriodConf,BudgetPeriodUnit)
from .forms import(ProjectBudgetForm,)

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
    if sd.day > 15:
        year = sd.year+1 if sd.month == 12 else sd.year
        sd = sd.replace(day=01,month = sd.month+1,year=year)
    ed = budgetobj.end_date
    no_of_quarters = ((ed.year - sd.year) * 12 + ed.month - sd.month)/3
    quarter_list = {}
    for i in range(no_of_quarters):
        ed = sd+timedelta(days=90)
        quarter_list.update({i:str(sd)+" to "+str(ed)})
        sd = ed
    return quarter_list

def projectlinetemadd(request):
    project_slug = request.GET.get('slug')
    projectobj =  Project.objects.get_or_none(slug=project_slug)
    budget_id = request.GET.get('budget_id')
    budgetobj = Budget.objects.get_or_none(id = budget_id )
    supercategory_list = SuperCategory.objects.filter(active=2,project =projectobj,budget = budgetobj)
    heading_list = MasterCategory.objects.filter(active=2)
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
                budget_period = value
                start_date = budget_period.split('to')[0].rstrip()
                end_date = budget_period.split('to')[1].lstrip()
                budget_periodobj = ProjectBudgetPeriodConf.objects.create(project = projectobj,budget = budgetobj,start_date=start_date,end_date=end_date,name = projectobj.name,row_order=int(i))
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
                print result
                if result["subheading"]:
                    budget_dict = {'created_by':UserProfile.objects.get_or_none(user_reference_id = int(request.session.get('user_id'))),
                               'budget_period':budget_periodobj,
                               'category':SuperCategory.objects.get_or_none(id = result['location']),
                               'heading':MasterCategory.objects.get_or_none(id = result['heading']),
                               'subheading':result['subheading'],
                               'unit':result['unit'],
                               'unit_type':result['unit-type'],
                               'rate':result['rate'],
                               'planned_unit_cost':result['planned-cost'],
                               'utilized_unit_cost':result['utilized-cost'],
                               'start_date':start_date,
                               'end_date':end_date,
                               'row_order':int(i),
                               'quarter_order':int(quarter),
                               }
                    budet_lineitem_obj = BudgetPeriodUnit.objects.create(**budget_dict)
                    print "budget line itme object" ,budet_lineitem_obj
        return HttpResponseRedirect('/project/list/')
    return render(request,"budget/budget_lineitem.html",locals())

from itertools import groupby
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
