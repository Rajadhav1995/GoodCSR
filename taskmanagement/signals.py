# Signals for survey
from django.dispatch import Signal, receiver
from django.db.models.signals import post_save, pre_save
from taskmanagement.models import *
from django.forms.models import model_to_dict
from django.core.cache import cache



@receiver(post_save, sender=Task)
def task_auto_updation_date(sender, **kwargs):
    task_obj = kwargs['instance']
    tasks = Task.objects.latest_one(task_dependency = task_obj.id)
    if tasks:
        tasks.start_date = task_obj.end_date
        tasks.save()
        
