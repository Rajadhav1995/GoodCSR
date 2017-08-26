from django.shortcuts import render
from django.template.defaultfilters import slugify
from django.http import HttpResponse,HttpResponseRedirect
from projectmanagement.models import (Project,)
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
            projectbudgetobj = Budget.objects.create(actual_start_date=request.POST.get("actual_start_date"),end_date=request.POST.get("end_date"),project= projectobj,financial_type=2,start_date = request.POST.get("actual_start_date") )
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
        projectobj =  Project.objects.get(slug=project_slug)
        budgetobj = Budget.objects.get_or_none(id = budget_id )
        supercategoryobj = SuperCategory.objects.create(name = request.POST.get('super-category'),project = projectobj)
        supercategoryobj.slug = slugify(supercategoryobj.name)
        supercategoryobj.save()
        category_names  = [str(k) for k,v in request.POST.items() if k.startswith('category')]
        for i in category_names:
            if request.POST.get(i):
                sub_categoryobj = SuperCategory.objects.create(name = request.POST.get(i),project = projectobj,parent=supercategoryobj)
                sub_categoryobj.slug = slugify(sub_categoryobj.name)
                sub_categoryobj.save()
        return HttpResponseRedirect('/manage/project/budget/lineitem/add/?slug='+str(project_slug)+'&budget_id='+str(int(budgetobj.id)))
    else:
        message = "Please fill the form properly"
    return render(request,"budget/budget_create.html",locals())

def projectlinetemadd(request):
    project_slug = request.GET.get('slug')
    budget_id = request.GET.get('budget_id')
    if request.method == "POST":
        pass
    else:
        message = "Please fill the form properly"
    return render(request,"budget/budget_lineitem.html",locals())

