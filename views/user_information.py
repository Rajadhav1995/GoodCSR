from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from projectmanagement.models import (UserProfile,)
from userprofile.models import (RoleTypes,UserRoles,ProjectUserRoleRelationship)
from ast import literal_eval
def get_user_role(userprofileobj):
    org_code = {'1':1,'2':2,'4':4,'0':3}
    code = org_code.get(str(userprofileobj.organization_type))
    roleobj = RoleTypes.objects.get(code = code)
    return roleobj


# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
class UserInformationStorage(APIView):

    def post(self, request, *args, **kwargs):
        data = request.data
        is_admin_user = True if str(request.data.get('is_admin_user')) == "True" else False
        owner = True if str(request.data.get('owner')) == "True" else False
        user_data = {'user_reference_id':data.get('user_reference_id'),
                    'email':data.get('email'),
                    'organization':data.get('organization'),
                    'organization_type':data.get('organization_type'),
                    'owner':owner,
                    'is_admin_user':is_admin_user,
                    'name':data.get('name'),
                    'designation':data.get('designation'),
                    'active':data.get('active'),
                    'attrs':literal_eval(data.get('attrs')),
                    }
        userprofileobj = UserProfile.objects.get_or_none(user_reference_id = data.get('user_reference_id'))
        if not userprofileobj:
            userprofileobj = UserProfile.objects.create(**user_data)
        else:
            userprofileobj.__dict__.update(user_data)
            userprofileobj.save()
        roleobj = get_user_role(userprofileobj)
        userroleobj,created = UserRoles.objects.get_or_create(user = userprofileobj)
        userroleobj.role_type.add(roleobj)
        userroleobj.email = userprofileobj.email
        userroleobj.save()
        response = {'msg':"created successfully",'status':2}
        return Response(response)

# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
def saveimage(request):
    url=request.META.get('HTTP_REFERER')
    return HttpResponseRedirect(url)

from django.http import HttpResponse
from django.views.generic import View

from budgetmanagement.utils import render_to_pdf #created in step 4
import datetime

class GeneratePdf(View):
    def get(self, request, *args, **kwargs):
     data = {
          'today': datetime.date.today(), 
          'amount': 39.99,
         'customer_name': 'Cooper Mann',
         'order_id': 1233434,
     }
     pdf = render_to_pdf('report/invoice.html', data)
     return HttpResponse(pdf, content_type='application/pdf')



def add_userroles():
    userprofileobj = UserProfile.objects.all()
    #import ipdb; ipdb.set_trace();
    for userobj in userprofileobj:
        roleobj = UserRoles.objects.get_or_none(user = userobj)
        if not roleobj:
            relationuser = list(ProjectUserRoleRelationship.objects.filter(user = userobj).values_list('role__id', flat=True).distinct())
            user_role_types_id = []
            if relationuser:
                user_role_types_id.extend(relationuser)
            roletypeobj = RoleTypes.objects.filter(id__in = user_role_types_id)
            userroleobj, created = UserRoles.objects.get_or_create(user = userobj)
            org_type_role = get_user_role(userobj)
            userroleobj.role_type.add(org_type_role)
            for ro in roletypeobj:
                userroleobj.role_type.add(ro)
            userroleobj.email = userobj.email
            userroleobj.save()
            #print ('userroles created')
        else:
            org_type_role = get_user_role(userobj)
            if org_type_role not in roleobj.role_type.all():
                roleobj.role_type.add(org_type_role)
                roleobj.save()
                #print ('main role added')
            
            
            
            
            
    
    

# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
