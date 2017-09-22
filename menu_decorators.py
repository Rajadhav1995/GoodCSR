# Custom Decorators defines here
from django.utils.decorators import method_decorator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import logout
from userprofile.models import *
from django.views.decorators.http import require_POST as post_only
import urllib



def has_menu_permission(object):
    # function to check user permission
    # user_obj user that is logged in
    # amenu checks all the permissions for the user
    # if user has a permission it will add to the menu list
    # if user is not superuser and menu list not found
    # redirect to invalid user page
    # only authenticated user function
    # path to which url should be redirected
    
    def haspermission(function):
        def is_auth(request, *args ,**kwargs):
            user = request.user
#            menu_list = Menus.objects.filter(active = 2).order_by('name')
            if user.is_authenticated():
                if not user.is_superuser:
                    path = request.path
                    if len(path.split('/')) == 5:
                        name = path.split('/')[2]
                        key = path.split('/')[3]
                    elif len(path.split('/')) == 6:
                        name = path.split('/')[3]
                        key = path.split('/')[4]
                        if key.isdigit():
                            name = path.split('/')[2]
                            key = path.split('/')[3]
                    elif len(path.split('/')) == 7:
                        return function(request, *args, **kwargs)
                    elif len(path.split('/')) < 5:
                        user_obj = UserRoles.objects.get(user=user)
                        roletypes = user_obj.role_type.all().values("id")
                        mlist = list(set(RoleConfig.objects.filter(active=2,view=2).filter(role__id__in=\
                                    roletypes).values_list('menu__link',flat=True)))
                        if path in mlist:
                            return function(request, *args, **kwargs)
                        else:
                            msg = "Oops Permission Denined!!!"
                            #return render(request, "manage/login.html", locals())
                            return function(request, *args, **kwargs)
                    path = request.path
                    user_obj = UserRoles.objects.get(user=user)
                    if user_obj:
                        roletypes = user_obj.role_type.all().values("id")
                        if name == "list":
                            mlist = list(set(RoleConfig.objects.filter(active=2,view=2).filter(role__id__in=\
                                    roletypes).values_list('menu__name',flat=True)))
                        elif name == "add":
                            mlist = list(set(RoleConfig.objects.filter(active=2,add=2,view=2).filter(role__id__in=\
                                    roletypes).values_list('menu__name',flat=True)))
                        elif name == "edit":
                            mlist = list(set(RoleConfig.objects.filter(active=2,edit=2,view=2).filter(role__id__in=\
                                    roletypes).values_list('menu__name',flat=True)))
                        new_mlist = [i.lower() for i in mlist]
                        if key in new_mlist:
                            return function(request, *args, **kwargs)
                        else:
                            msg = "Oops Permission Denined!!!"
                            return render(request, "manage/login.html", locals())
                    else:
                        return HttpResponseRedirect("/")
            else:
                return HttpResponseRedirect("/")
#            except:
#                return HttpResponseRedirect(str(request.path))
            return function(request, *args, **kwargs)
        return is_auth
    object.dispatch = method_decorator(haspermission)(object.dispatch)
    return object



#function for checking allowed access
# function based views
def check_allowed_access(view):
#checks if the request is auth
    def is_auth(request, *args, **kwargs):
        user = request.user
#checks the user is superuser
        if user.is_authenticated():
            if not user.is_superuser:
                path = request.path
                if len(path.split('/')) == 5:
                    name = path.split('/')[2]
                    key = path.split('/')[3]
                    user_obj = UserRoles.objects.get(user=user)
                    roletypes = user_obj.role_type.all().values("id")
                    mlist = list(set(RoleConfig.objects.filter(active=2,view=2).filter(role__id__in=\
                                roletypes).values_list('menu__link',flat=True)))
                    if path in mlist:
                        return view(request, *args, **kwargs)
                    else:
                        msg = "Oops Permission Denined!!!"
                        return render(request, "manage/login.html", locals())
                else:
                    return HttpResponseRedirect("/")
            else:
                return view(request, *args, **kwargs)
        else:
            return HttpResponseRedirect("/")
        return view(request, *args, **kwargs)
        
    return is_auth


def check_loggedin_access(view):
    def is_auth(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        return view(request, *args, **kwargs)
    return is_auth



