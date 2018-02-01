from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from projectmanagement.models import (UserProfile,)
from userprofile.models import (RoleTypes,UserRoles)

def get_user_role(userprofileobj):
    org_code = {'1':1,'2':2,'4':4,'0':3}
    code = org_code.get(str(userprofileobj.organization_type))
    roleobj = RoleTypes.objects.get(code = code)
    return roleobj

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
                    'attrs':eval(data.get('attrs')),
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
