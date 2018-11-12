from django.db import models
from django.utils.encoding import smart_str, smart_unicode
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

# Activity model
class Activity(BaseContent):
    project = models.ForeignKey("projectmanagement.Project",**OPTIONAL)
    super_category = models.ForeignKey("budgetmanagement.SuperCategory",**OPTIONAL)
    name = models.CharField(max_length=600,**OPTIONAL)
    activity_type = models.IntegerField(choices = ACTIVITY_CHOICES,default=1)
    status = models.IntegerField( choices = STATUS_CHOICES,default=0)
    description = models.TextField(**OPTIONAL)
    created_by = models.ForeignKey("projectmanagement.UserProfile",related_name ='activity_created_user',blank=True,null=True)
    assigned_to = models.ForeignKey("projectmanagement.UserProfile",related_name ='activity_asigned_user',blank=True,null=True)
    subscribers = models.ManyToManyField("projectmanagement.UserProfile",related_name = 'activity_subscriber_user',blank=True )
    slug = models.SlugField(_("Slug"), max_length=600,blank=True)
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s",**OPTIONAL)
    object_id = models.IntegerField(_('object ID'),**OPTIONAL)
    relatedTo = GenericForeignKey(ct_field="content_type", fk_field="object_id")
    history = HistoricalRecords()
    
    def __str__(self):
        return str(self.name)
    def __unicode__(self):
        return unicode(self.name)

# task model
class Task(BaseContent):
    name = models.CharField(max_length=600,**OPTIONAL)
    activity = models.ForeignKey(Activity)
    start_date=models.DateTimeField(**OPTIONAL)
    end_date=models.DateTimeField(**OPTIONAL)
    slug = models.SlugField(_("Slug"), max_length=600,blank=True)
    actual_start_date = models.DateTimeField(**OPTIONAL)
    actual_end_date = models.DateTimeField(**OPTIONAL)
    status = models.IntegerField(choices = STATUS_CHOICES,default=0)
    task_dependency = models.ManyToManyField('self',blank=True,symmetrical=False)
    created_by = models.ForeignKey("projectmanagement.UserProfile",related_name ='task_created_user',**OPTIONAL)
    assigned_to = models.ForeignKey("projectmanagement.UserProfile",related_name ='task_assigned_user',blank=True,null=True)
    subscribers = models.ManyToManyField("projectmanagement.UserProfile",related_name = 'task_subscriber_user',blank=True )
    task_progress = models.CharField(max_length=100,**OPTIONAL)
    history = HistoricalRecords()

    def __str__(self):
        return smart_str(self.name) or ''
    def __unicode__(self):
        return unicode(self.name)

    def is_dependent(self):
        task = Task.objects.filter(task_dependency = self.id)
        if task:
            return True
        else :
            return False
    
    def task_attachments(self):
        inner_attach=[]
        from datetime import datetime
        from media.models import Attachment,Comment
        comment = Comment.objects.filter(active=2,content_type=ContentType.objects.get(model=('task')),object_id=self.id).order_by('-id')
        comment_dates = list(set([i.date() for i in comment.values_list('created',flat=True)]))
        task_progress_history = self.history.filter(task_progress__isnull=False).order_by('-id')
        attachments = Attachment.objects.filter(active=2,content_type=ContentType.objects.get(model=('task')),object_id=self.id).order_by('-id')
        attach_dates = list(set([i.date() for i in attachments.values_list('modified',flat=True)]))
        task_progress_dates = list(set([i.date() for i in task_progress_history.values_list('modified',flat=True)]))
        
        distinct_dates = attach_dates + comment_dates + task_progress_dates
        
        attach = []
        if distinct_dates:
            for date in list(set(distinct_dates)):
                inner_attach =[]
                for i in attachments.filter(created__range = (datetime.combine(date, datetime.min.time()),datetime.combine(date, datetime.max.time()))):
                    inner_attach.append(i)
                attach.append({date:inner_attach})
            attach = sorted(attach, key=lambda key: key,reverse=True)
        else:
            attach=[]
        return attach

# milestone model
class Milestone(BaseContent):
    project = models.ForeignKey("projectmanagement.Project",**OPTIONAL)
    name = models.CharField(max_length=300,**OPTIONAL)
    task = models.ManyToManyField(Task,blank=True)
    overdue = models.DateTimeField(**OPTIONAL)
    status = models.IntegerField(choices = STATUS_CHOICES,default=0)
    slug = models.SlugField(_("Slug"), max_length=600,blank=True)
    subscribers = models.ManyToManyField("projectmanagement.UserProfile",related_name = 'milestone_subscriber_user',blank=True )
    history = HistoricalRecords()
    def __str__(self):
        return smart_str(self.name)
    def __unicode__(self):
        return unicode(self.name)

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
