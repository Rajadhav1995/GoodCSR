from django import template
from django.contrib.auth.models import User
from userprofile.models import Menus, RoleConfig, RoleTypes, UserRoles

register = template.Library()

# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.

@register.filter
def get_all_menus(value):
    #
    # filtering active menus
    #
    return Menus.objects.filter(active = 2).order_by('name')


@register.filter
def get_role_config_obj(value, rid):
    try:
        return RoleConfig.objects.get(menu__id = value, role__id = rid)
    except:
        return None


@register.filter
def get_user_menu_list(request):
    user = request.user.id or None
    menu_list = []
    if user is not None:
        user_role = UserRoles.objects.get(user__id = user)
        role_ids = user_role.role_type.all().values_list('id', flat = True)
        role_configs = RoleConfig.objects.filter(role__id__in = role_ids,
                        view = 2).order_by('menu__name')
        menu_ids = list(set(role_configs.values_list('menu__id', flat = True)))
        menus = Menus.objects.filter(id__in = menu_ids, active = 2).distinct()
        parent_menus = menus.filter(parent = None)
        menu_list = [(menu, 
                        [(menu1, 
                            [(menu2, 
                                [(menu3, menus.filter(parent=menu3))
                                    for menu3 in menus.filter(parent = menu2)])
                                for menu2 in menus.filter(parent = menu1)])
                            for menu1 in menus.filter(parent = menu)])
                        for menu in parent_menus]

    return menu_list

# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
@register.filter
def has_permission_for_action(request, key):
     
    # 
    # Check for the permission of user for the action of menu 
    # 
    
    user = request.user or None
    menu, permission_key = key.split('&')
    success = False
    if user is not None:
        user_role = UserRoles.objects.get(user = user)
        for role in user_role.role_type.all():
            role_config = RoleConfig.objects.get(role = role,
                        menu__slug = menu)
            if getattr(role_config, permission_key):
                success = True
                break

    return success

# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
@register.filter
def make_string(val1, val2):
    return val1+"&"+val2

# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
@register.assignment_tag
def check_menu_permission(user,menuname):

    # 
    # to check for the permission of user for the menu section
    #
#    import ipdb;ipdb.set_trace()
    status = False
    if user and menuname:
        try:
            user_obj = UserRoles.objects.get(user=user)
        except:
            user_obj = None
        if user_obj:
            roletypes = user_obj.role_type.all().values("id")
            mlist = list(set(RoleConfig.objects.filter(active=2).filter(role__id__in=\
                                            roletypes).values_list('menu__name',flat=True)))
            new_mlist = [i.lower() for i in mlist]
            if menuname in new_mlist:
                status = True
    if user.is_superuser:
        status = True
    return status
# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
@register.assignment_tag
def get_menu_list():
    menu = Menus.objects.filter(parent=None)
    return menu

# Without it, things can get real confusing, real fast.