from django.shortcuts import render
from projectmanagement.models import UserProfile
from django.contrib.auth.models import User

#create views of dashboard

def admin_dashboard(request):
    user_id = request.session.get('user_id')
    user_obj = UserProfile.objects.get(user_reference_id = user_id )
#    user = User.objects.get(id = user_obj.id )
    return render(request,'base.html')

