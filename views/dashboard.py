from django.shortcuts import render

#create views of dashboard

def admin_dashboard(request):
    user_id = request.session.get('user_id')
    return render(request,'base.html')

