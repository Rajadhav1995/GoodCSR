# Signals for survey
from django.dispatch import Signal, receiver
from django.db.models.signals import post_save, pre_save
from taskmanagement.models import *
from django.forms.models import model_to_dict
from django.core.cache import cache
from projectmanagement.models import Project
from budgetmanagement.models import Budget
from media.models import Attachment
from django.core.signals import got_request_exception

user_login = Signal(providing_args=["request", "user"])


# @receiver(post_save, sender=Task)
# def task_auto_updation_date(sender, **kwargs):
#     task_obj = kwargs['instance']
#     tasks = Task.objects.latest_one(task_dependency = task_obj.id)
#     if tasks:
#         tasks.start_date = task_obj.end_date
#         tasks.save()
        
# @receiver(post_save, sender=Task)
# def milestone_completion_status(sender,**kwargs):
# #this is to close the milestone based on the closed task of that milestone 
#     task_obj = kwargs['instance']
#     task = Task.objects.latest_one(id=task_obj.id,status=2)
#     miles = Milestone.objects.filter(task = task)
#     for i in miles:
#         mile_obj = Milestone.objects.get(id = i.id)
#         tasks = mile_obj.task
#         if tasks.filter(status =2).count()==tasks.count():
#             mile_obj.status=2
#             mile_obj.save()
        
# @receiver(post_save, sender=Budget)
# @receiver(post_save, sender=Project)
# @receiver(post_save, sender=Task)
# @receiver(post_save, sender=Attachment)
# @receiver(got_request_exception)

# def save_modified_by_users(sender, **kwargs):
#     obj = kwargs['instance']
# #    inst = receiver_function(sender, request)
