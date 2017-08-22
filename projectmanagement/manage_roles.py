from django.shortcuts import render
from  django.http import HttpResponse,HttpResponseRedirect
from projectmanagement.models import (Project,)
from userprofile.models import (ProjectUserRoleRelationship,)
from .forms import(ProjectUserRoleRelationshipForm,)


def projectuserslist(request):
    project_slug = request.GET.get('slug')
    projectuserlist = ProjectUserRoleRelationship.objects.filter(project__slug=project_slug)
    return render(request,'project/project_user_list.html',locals())

def projectuseradd(request):
    key = "add"
    project_slug = request.GET.get('slug')
    form = ProjectUserRoleRelationshipForm()
    if request.method == "POST":
        project_slug = request.POST.get('slug')
        projectobj =  Project.objects.get(slug=project_slug)
        form1 = ProjectUserRoleRelationshipForm(request.POST,request.FILES)
        if form1.is_valid():
            form = form1.save(commit=False)
            projectuserobj = form1.save()
            projectuserobj.project = projectobj
            projectuserobj.save()
            msg = "form is submitted" 
            return HttpResponseRedirect('/manage/project/role/list/?slug='+str(project_slug))
        else :
            msg = "Please fill the form properly"
    return render(request,'project/manage_project_user.html',locals())

def projectuseredit(request):
    key = "edit"
    objid = request.GET.get('objid')
    project_slug = request.GET.get('slug')
    pmobj = ProjectUserRoleRelationship.objects.get(id=int(objid))
    form = ProjectUserRoleRelationshipForm(instance = pmobj)
    if request.POST:
        project_slug = request.POST.get('slug')
        form = ProjectUserRoleRelationshipForm(request.POST, instance = pmobj)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/manage/project/role/list/?slug='+str(project_slug))
        else:
            msg = "Email Already exists"
    return render(request,'project/manage_project_user.html',locals())
