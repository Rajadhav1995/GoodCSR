from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from projectmanagement.models import (UserProfile,)

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
        response = {'msg':"created successfully",'status':2}
        return Response(response)
