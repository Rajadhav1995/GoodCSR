from django.shortcuts import render

#create views of dashboard

def admin_dashboard(request):
    return render(request,'base.html')
    
