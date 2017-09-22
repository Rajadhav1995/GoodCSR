# Custom Decorators defines here
from django.utils.decorators import method_decorator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import logout
from userprofile.models import *
from django.views.decorators.http import require_POST as post_only
import urllib

def check_loggedin_access(view):
    def is_auth(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        return view(request, *args, **kwargs)
    return is_auth



