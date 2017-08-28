from django.shortcuts import render
from datetime import timedelta
from django.template.defaultfilters import slugify
from django.http import HttpResponse,HttpResponseRedirect
from projectmanagement.models import (Project,MasterCategory)
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

def projectlinetemadd(request):
    project_slug = request.GET.get('slug')
    projectobj =  Project.objects.get_or_none(slug=project_slug)
    budget_id = request.GET.get('budget_id')
    budgetobj = Budget.objects.get_or_none(id = budget_id )
    supercategory_list = SuperCategory.objects.filter(active=2,project =projectobj,budget = budgetobj)
    heading_list = MasterCategory.objects.filter(active=2)
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
#    quater_list = ['may-2017 to july-2017','august-2017 to october-2017','nov-2017 to jan-2017','feb-2017 to april-2017']
    if request.method == "POST":
        pass
    return render(request,"budget/budget_lineitem.html",locals())

