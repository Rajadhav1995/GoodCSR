from django.shortcuts import render
from userprofile.models import *
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import Http404
from django.apps import apps
from django.http import JsonResponse
from django.views.generic.edit import CreateView, UpdateView, DeleteView 
from django.views.generic.list import ListView
from django.http import HttpResponseRedirect, HttpResponse, Http404


class Manage(object):

    def get_model(self):
    #--------------------------------------------#
    # get_model function to return model name using dictionary
    # model_name is a dictionary
    #-----------------------------------------#
        model_name = {
            'role': 'RoleTypes',
            'user': 'UserRoles',
            'menu':"Menus",
            'roleconfig':"RoleConfig",
        }[self.kwargs['model']]
        return apps.get_model('userprofile.%s' %(model_name))
        
    def get_queryset(self):
    #--------------------------------------#
    # queryset to get objects based on model
    # if a model name is roleconfig then filter based on role
    #---------------------------------------#
        if self.kwargs['model'] == 'roleconfig':
            return self.get_model().objects.filter(role_id=self.kwargs['pid'])
        if self.kwargs['model'] == 'role':
            return self.get_model().objects.filter(active=2)
        return self.get_model().objects.all()

    def get_context_data(self, **kwargs):
        context = super(Manage, self).get_context_data(**kwargs)
        context['model'] =  self.kwargs['model']
        context['request'] =  self.request
        if self.kwargs['model'] == 'roleconfig':
            context['pid'] =  self.kwargs['pid']
        user = self.request.user
        if not user.is_superuser and self.kwargs['model'] == 'role':
            context['object_list'] = RoleTypes.objects.exclude(name__iexact = "Application admin")                            
        return context

    def get_form(self, form_class=None):
    #--------------------------------------#
    # get_form method is a common method to get form names
    # 3 model: menu,roleconfig and role 
        form = super(Manage, self).get_form(form_class)
        from django import forms
        if self.kwargs['model'] == 'menu':
            form.fields['parent'].widget = forms.Select(attrs= {'class':'form-control'})
            form.fields['parent'].queryset = Menus.objects.all()
            form.fields['link'].widget = forms.TextInput(attrs= {'class':'form-control'})
            form.fields['menu_order'].widget = forms.TextInput(attrs= {'class':'form-control'})
            form.fields['name'].widget = forms.TextInput(attrs= {'class':'form-control'})
        if self.kwargs['model'] == 'roleconfig':
            form.fields['menu'].widget = forms.Select(attrs= {'class':'form-control'})
            form.fields['menu'].queryset = Menus.objects.all()

        if self.kwargs['model'] == 'role':
            form.fields['name'].widget = forms.TextInput(attrs= {'class':'form-control'})


        return form

    def form_valid(self, form):
    #----------------------------#
    # common form valid method for validating form
    #---------------------------#
    
        if self.kwargs['model'] == 'roleconfig':
            self.object = form.save(commit=False)
            self.object.role=Role_Types.objects.get(pk=self.kwargs['pid'])
            self.object.save()
            return HttpResponseRedirect('/usermanagement/list/roleconfig/%s/'%(str(self.kwargs['pid'])))
        elif self.kwargs['model'] == 'user':
            self.object = form.save(commit=False)
            self.object_email = User.objects.filter(email=self.request.POST.get('email'))
            if self.object_email:
                form.add_error('email', "Email already exists")
                return self.form_invalid(form)
            else:
                self.object = form.save()
        else:
            self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


    def get_success_url(self):
    #-----------------------------#
    # on success returning to particular model list
    #--------------------------------#
        return "/close/?msg=%s added successfully." %(self.kwargs['model'])




class UserListView(Manage, ListView):
    # class based method is used for listing
    
    template_name = 'usermanagement/list.html'


class UserAddView(Manage, CreateView):
    #-----------------------------------------#
    # class based method to add user,menu,roleconfig
    
    template_name = 'usermanagement/add-edit.html'
    success_url = '/usermanagement/list/role/'

    def get_form_class(self):
        self.fields = ['name']
        if self.kwargs['model'] == 'user':
            self.fields = ['first_name', 'last_name', 'email', 'role_type',]
          
        if self.kwargs['model'] == 'menu':
            self.fields = ['name','parent', 'link', 'menu_order' ]
        if self.kwargs['model'] == 'roleconfig':
            self.fields = ['menu', 'view','add', 'edit','delete' ]
        return super(UserAddView, self).get_form_class()


class UserEditView(Manage, UpdateView):
    #-----------------------------#
    #class based method to edit form
    # model: user,menu,roleconfig
    #------------------------------#
    template_name = 'usermanagement/add-edit.html'

    def get_form_class(self):
        self.fields = ['name']
        if self.kwargs['model'] == 'user':
            self.fields = ['first_name', 'last_name', 'email', 'role_type', ]
        if self.kwargs['model'] == 'menu':
            self.fields = ['name','parent', 'link', 'menu_order' ]
        if self.kwargs['model'] == 'roleconfig':
            self.fields = ['menu', 'view','add', 'edit','delete' ]
        return super(UserEditView, self).get_form_class()


class UserActive(Manage, DeleteView):
    #class based method to activate and deactivate objects for all models
    

    def dispatch(self, *args, **kwargs):

        self.get_object().switch()
        return HttpResponseRedirect(self.request.META['HTTP_REFERER'])
        


def manage_role(request, pk):
    #-------------------------#
    # managing roles of user 
    # --------------#
    role = RoleTypes.objects.get(pk=pk)
    confs = [i for i in role.get_role_config()]

    if request.method == 'POST':
        perm_data = [(conf, request.POST.getlist(str(conf.id)))
                     for conf in confs]
        # [
        #     (<Role_Config: Masterdata>, [u'view']),
        #     (<Role_Config: Donor>, [u'add', u'edit']),
        #     (<Role_Config: salutation>, [])
        # ]
        for conf,perms in perm_data:
            if 'edit' in perms or 'add' in perms and 'view' != perms :
                perms.append('view')
                conf.update(perms)

            elif 'delete' in perms and 'view'!= perms and 'edit'!= perms:
                perms.append('view')
                perms.append('edit')
                conf.update(perms)

            else:
                conf.update(perms)

            parent = conf.menu.parent
            if parent and perms:
                roleconf = RoleConfig.objects.filter(menu=parent,role=role)[0]
                if roleconf:
                    roleconf.update('view')
    return render(request, 'usermanagement/manage-role.html', locals())


def manage_menu(request, pk):
    #-------------------------#
    # managing roles of user 
    role = RoleTypes.objects.get(pk=pk)
    confs = [i[0] for i in role.get_menu_config()]
    model = "RoleConfig"

    return render(request, 'usermanagement/manage-menu.html', locals())

def object_active(request,pk):

    # Activate or deactivate a model object
    # Then redirect to listing page


        obj=RoleConfig.objects.get(pk=pk)
        obj.switch()
        obj.save()
        return JsonResponse({'status': obj.active})
