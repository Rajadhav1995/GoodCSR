# Signals for survey
from django.dispatch import Signal, receiver
from django.db.models.signals import post_save, pre_save
from taskmanagement.models import *
from django.forms.models import model_to_dict
from django.core.cache import cache
from projectmanagement.models import Project
from budgetmanagement.models import *
from media.models import Attachment,Comment
from django.core.signals import got_request_exception

# Django provides a range of tools and libraries 
# to help you build forms to accept input from 
# site visitors, and then process and respond to the input.
'''This is to update the tasks object startdate and end date'''
@receiver(post_save, sender=Task)
def task_auto_updation_date(sender, **kwargs):
    task_obj = kwargs['instance']
    tasks = Task.objects.latest_one(task_dependency = task_obj.id)
    if tasks:
        tasks.start_date = task_obj.end_date
        tasks.save()

# Django provides a range of tools and libraries 
# to help you build forms to accept input from 
# site visitors, and then process and respond to the input.
'''This is to close the milestone , if aany of the task is closed which
is related to a milestone checking whether that milestone othertasks
are also closed if so then close the milestone otherwise the status of milestone is open'''
@receiver(post_save, sender=Task)
def milestone_completion_status(sender,**kwargs):
#this is to close the milestone based on the closed task of that milestone 
# Django provides a range of tools and libraries 
# to help you build forms to accept input from 
# site visitors, and then process and respond to the input.
    task_obj = kwargs['instance']
    task = Task.objects.latest_one(id=task_obj.id,status=2)
    miles = Milestone.objects.filter(task = task)
    for i in miles:
        mile_obj = Milestone.objects.get(id = i.id)
        tasks = mile_obj.task
        if tasks.filter(status =2).count()==tasks.count():
            mile_obj.status=2
            mile_obj.save()

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