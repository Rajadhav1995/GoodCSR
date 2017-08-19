from django.db import models
from projectmanagement.manager import ActiveQuerySet
from django.template.defaultfilters import slugify
from constants import  OPTIONAL
import six
from django.contrib import admin
from django.views import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from simple_history.models import HistoricalRecords
from thumbs import ImageWithThumbsField
from simple_history.admin import SimpleHistoryAdmin
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from projectmanagement.models import BaseContent

#----------------------introduction------------------------------------------#
# Task Management is the application where database tables are related to Activity,Task,Milestone
#--------------------ends here--------------------------------------------------#

ACTIVITY_CHOICES = ((1,'Core'),(2,'Non-core'),)
STATUS_CHOICES = ((0,' '),(1, 'Open'), (2, 'Close'), (3, 'Ongoing'),)


class Activity(BaseContent):
    project = models.ForeignKey("projectmanagement.Project",**OPTIONAL)
    super_category = models.ForeignKey("budgetmanagement.SuperCategory",**OPTIONAL)
    name = models.CharField(max_length=600,**OPTIONAL)
    activity_type = models.IntegerField(choices = ACTIVITY_CHOICES,default=1)
    status = models.IntegerField( choices = STATUS_CHOICES,default=0)
    description = models.TextField(**OPTIONAL)
    created_by = models.ForeignKey("projectmanagement.UserProfile",related_name ='activity_created_user',blank=True,null=True)
    assigned_to = models.ForeignKey("projectmanagement.UserProfile",related_name ='activity_subscriber_user',blank=True,null=True)
    slug = models.SlugField(_("Slug"), blank=True)
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s",**OPTIONAL)
    object_id = models.IntegerField(_('object ID'),**OPTIONAL)
    relatedTo = GenericForeignKey(ct_field="content_type", fk_field="object_id")
    history = HistoricalRecords()

class Task(BaseContent):
    name = models.CharField(max_length=600,**OPTIONAL)
    activity = models.ForeignKey(Activity)
    start_date=models.DateTimeField(**OPTIONAL)
    end_date=models.DateTimeField(**OPTIONAL)
    slug = models.SlugField(_("Slug"), blank=True)
    actual_start_date = models.DateTimeField(**OPTIONAL)
    actual_end_date = models.DateTimeField(**OPTIONAL)
    status = models.IntegerField(choices = STATUS_CHOICES,default=0)
    created_by = models.ForeignKey("projectmanagement.UserProfile",related_name ='task_created_user',**OPTIONAL)
    assigned_to = models.ForeignKey("projectmanagement.UserProfile",related_name ='task_assigned_user',blank=True,null=True)
    history = HistoricalRecords()

class Milestone(BaseContent):
    name = models.CharField(max_length=300,**OPTIONAL)
    task = models.ManyToManyField(Task,blank=True)
    overdue = models.DateTimeField(**OPTIONAL)
    history = HistoricalRecords()
