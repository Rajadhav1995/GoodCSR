from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse,HttpResponseRedirect
from pmu.settings import HOST_URL, PHOTO_URL

# Create your views here.

def Listing(request,model_name):

    obj = eval(model_name).objects.all().order_by('-id')
    return render(request,'listing.html',locals())
    


def loginpage(request):
    if request.method == 'GET':
        return render(request,'login.html')
    if request.method == 'POST':
        user = authenticate(username = request.POST.get('username'), password = request.POST.get('password'))
        if user is not None :
            if user.is_active and user.is_superuser:
                login(request, user)
                return HttpResponseRedirect('/masterdata/admin/')
            else:
                message = "Unauthorised User"
        else:
            message = "Invalid Username or Password"
    return render(request, 'login.html', locals())
    
def logouta(request):
    # function to logout and redirect to loginpage
    logout(request)
    return HttpResponseRedirect('/')
