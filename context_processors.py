from django.core.cache import cache
from projectmanagement.models import *
from django.contrib.auth.models import User


def global_variables(request):
    import ipdb;ipdb.set_trace()
    user_obj = UserProfile.objects.get(user_reference_id = request.session.get('user_id'))
    cache.set('user', user_obj)
