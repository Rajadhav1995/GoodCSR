from django.shortcuts import render
from  django.http import HttpResponse,HttpResponseRedirect
from projectmanagement.models import (Project,)
from userprofile.models import (ProjectUserRoleRelationship,UserRoles)
from .forms import(ProjectUserRoleRelationshipForm,)
from projectmanagement.models import ProjectFunderRelation,UserProfile
from menu_decorators import check_loggedin_access
# this section is to manage role wise access to different functionalities

def projectuserslist(request):
    '''
    This function is to add show project list, created by logged in user and it will show all project list to admin
    '''
    project_slug = request.GET.get('slug')
    projectuserlist = ProjectUserRoleRelationship.objects.filter(active=2,project__slug=project_slug)
    return render(request,'project/project_user_list.html',locals())

@check_loggedin_access
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
            userroleobj,created = UserRoles.objects.get_or_create(user = projectuserobj.user)
            userroleobj.role_type.add(projectuserobj.role)
            userroleobj.email = projectuserobj.user.email
            userroleobj.save()
            msg = "form is submitted"
            if str(redirect_key) == "summary":
                return HttpResponseRedirect('/project/summary/?slug='+str(project_slug))
            return HttpResponseRedirect('/manage/project/role/list/?slug='+str(project_slug))
        else :
            msg = "Please fill the form properly"
    return render(request,'project/manage_project_user.html',locals())

@check_loggedin_access
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
        # import ipdb; ipdb.set_trace()
        form = ProjectUserRoleRelationshipForm(request.POST, instance = pmobj)
        if form.is_valid():
            projectuserobj = form.save()
            userroleobj,created = UserRoles.objects.get_or_create(user = projectuserobj.user)
            userroleobj.role_type.add(projectuserobj.role)
            userroleobj.email = projectuserobj.user.email
            userroleobj.save()
            if str(redirect_key) == "summary":
                return HttpResponseRedirect('/project/summary/?slug='+str(project_slug))
            return HttpResponseRedirect('/manage/project/role/list/?slug='+str(project_slug))
        else:
            msg = "Email Already exists"
    return render(request,'project/manage_project_user.html',locals())

def manage_funder_relation(request):
    key = 'project_edit_user'
    project_slug = request.GET.get('slug')
    try:
        project_funder = request.GET.get('key')
    except Exception as e:
        e.message
    proj_obj = Project.objects.get(slug=project_slug)
    proj_funder_obj = ProjectFunderRelation.objects.get(project=proj_obj)
    funder_user = UserProfile.objects.filter(active=2,organization_type=1)
    partner = UserProfile.objects.filter(active=2,organization_type=2)
    if request.POST:
        slug = request.POST.get('slug')
        implementation_partner = int(request.POST.get('implementation_partner'))
        funder = int(request.POST.get('funder'))
        # import ipdb; ipdb.set_trace()
        proj_funder_obj.implementation_partner = UserProfile.objects.get(id=implementation_partner)
        proj_funder_obj.funder = UserProfile.objects.get(id=funder)
        proj_funder_obj.save()
        return HttpResponseRedirect('/project/summary/?slug='+str(project_slug))
    return render(request,'project/manage_project_user.html',locals())
