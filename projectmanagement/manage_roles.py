from django.shortcuts import render
from  django.http import HttpResponse,HttpResponseRedirect
from projectmanagement.models import (Project,)
from userprofile.models import (ProjectUserRoleRelationship,)
from .forms import(ProjectUserRoleRelationshipForm,)
# this section is to manage role wise access to different functionalities

def projectuserslist(request):
    '''
    This function is to add show project list, created by logged in user and it will show all project list to admin
    '''
    project_slug = request.GET.get('slug')
    projectuserlist = ProjectUserRoleRelationship.objects.filter(active=2,project__slug=project_slug)
    return render(request,'project/project_user_list.html',locals())

def projectuseradd(request):
    '''
    This function is to add user
    '''
    key = "add"
    redirect_key = request.GET.get('key')
    project_slug = request.GET.get('slug')
    form = ProjectUserRoleRelationshipForm()
    if request.method == "POST":
        redirect_key = request.POST.get('key')
        project_slug = request.POST.get('slug')
        projectobj =  Project.objects.get(slug=project_slug)
        form1 = ProjectUserRoleRelationshipForm(request.POST,request.FILES)
        if form1.is_valid():
            form = form1.save(commit=False)
            projectuserobj = form1.save()
            projectuserobj.project = projectobj
            projectuserobj.save()
            msg = "form is submitted"
            if str(redirect_key) == "summary":
                return HttpResponseRedirect('/project/summary/?slug='+str(project_slug))
            return HttpResponseRedirect('/manage/project/role/list/?slug='+str(project_slug))
        else :
            msg = "Please fill the form properly"
    return render(request,'project/manage_project_user.html',locals())

def projectuseredit(request):
    '''
    This function is to edit user
    '''
    key = "edit"
    redirect_key = request.GET.get('key')
    objid = request.GET.get('objid')
    project_slug = request.GET.get('slug')
    pmobj = ProjectUserRoleRelationship.objects.get(id=int(objid))
    form = ProjectUserRoleRelationshipForm(instance = pmobj)
    if request.POST:
        redirect_key = request.POST.get('key')
        project_slug = request.POST.get('slug')
        form = ProjectUserRoleRelationshipForm(request.POST, instance = pmobj)
        if form.is_valid():
            form.save()
            if str(redirect_key) == "summary":
                return HttpResponseRedirect('/project/summary/?slug='+str(project_slug))
            return HttpResponseRedirect('/manage/project/role/list/?slug='+str(project_slug))
        else:
            msg = "Email Already exists"
    return render(request,'project/manage_project_user.html',locals())
