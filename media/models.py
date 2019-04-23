import os,datetime,urllib
from django.db import models
from django.contrib import admin
from constants import OPTIONAL
from thumbs import ImageWithThumbsField
from django.views import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from ckeditor.fields import RichTextField
from budgetmanagement.models import (ReportParameter, BudgetPeriodUnit, ProjectBudgetPeriodConf, ReportMilestoneActivity)
from projectmanagement.models import (BaseContent,UserProfile, Project)
from private_storage.fields import PrivateFileField
from taskmanagement.models import (Task,Activity)
from simple_history.models import HistoricalRecords
from simple_history.admin import SimpleHistoryAdmin
# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
ATTACHMENT_TYPE = ((1,'Image'),(2,'Documents'),)
DOCUMENT_TYPE = ((1,'Excel'),(2,'PDF'),(3,'PPT'),(4,'Word Document'))

def get_file_path(instance,filename):
    from budgetmanagement.models import Answer
    print type(instance)
    date = datetime.datetime.today().strftime('%Y/%m/%d')
    try:
        if isinstance(instance, Attachment):
            if instance.content_type == ContentType.objects.get(model="project"):
                proj = Project.objects.filter(id=instance.object_id).first()
                proj_slug = proj.slug
            if instance.content_type == ContentType.objects.get(model="budgetperiodunit"):
                budget_period = BudgetPeriodUnit.objects.filter(id=instance.object_id).first()
                proj_slug = budget_period.budget_period.project.slug
            if instance.content_type == ContentType.objects.get(model="projectbudgetperiodconf"):
                budget_period = ProjectBudgetPeriodConf.objects.filter(id=instance.object_id).first()
                proj_slug = budget_period.project.slug
            if instance.content_type == ContentType.objects.get(model="task"):
                task = Task.objects.filter(id=instance.object_id).first()
                proj_slug = task.activity.project.slug
            if instance.content_type == ContentType.objects.get(model="reportmilestoneactivity"):
                report_ma = ReportMilestoneActivity.objects.filter(id=instance.object_id).first()
                proj_slug = report_ma.quarter.project.project.slug
        if isinstance(instance, Note):
            proj_slug = instance.project.slug
        if isinstance(instance, Answer):
            proj = Project.objects.filter(id=instance.object_id).first()
            proj_slug = proj.slug
        return "{proj_name}/{date}/{file}".format(proj_name = proj_slug, date = date, file = filename)    
    except Exception as e:
        return "other/{date}/{file}".format(date = date, file = filename)


class Attachment(BaseContent):
    ## 
    # model to attach files.
    #content_type is a foriegn key, verbose_name- is a function differing with _"
    ## 
        
    created_by = models.ForeignKey(
        UserProfile, related_name='document_created_user', **OPTIONAL)
    attachment_file = PrivateFileField(upload_to=get_file_path,max_length=500, **OPTIONAL)
    name = models.CharField("Name", max_length=300, **OPTIONAL)
    description = models.CharField("Description", max_length=600, **OPTIONAL)
    attachment_type = models.IntegerField('ATTACHMENT_TYPE',choices=ATTACHMENT_TYPE,**OPTIONAL)
    document_type = models.IntegerField('DOCUMENT_TYPE',choices = DOCUMENT_TYPE,**OPTIONAL)
    date = models.DateTimeField(**OPTIONAL)
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s",db_index=True, **OPTIONAL)
    object_id = models.IntegerField(_('object ID'), db_index=True, **OPTIONAL)
    relatedTo = GenericForeignKey(ct_field="content_type", fk_field="object_id")
    URL = models.URLField("Link url", max_length=200, blank=True)
    parent = models.ForeignKey('self', blank=True, null=True)
    timeline_progress = models.BooleanField(default=True)
    history = HistoricalRecords()

    def __unicode__(self):
        return str(self.id) or self.object_id

    def get_sub_documents(self):
        # 
        try:
            subdocuments = Attachment.objects.filter(active=2,parent=self)
            documents = [{'name':i.name,'file':PHOTO_URL+'/'+i.organisationdocument.document.url} for i in subdocuments]
        except:
            documents = []
            # 
        return documents

    def get_file_keywords(self):
        # 
        keywords = FileKeywords.objects.filter(active=2,object_id=self.id,content_type=ContentType.objects.get(model='Attachment')).values_list('key',flat=True)
        key_list = Keywords.objects.filter(id__in=keywords).values_list('name',flat=True)
        # 
        return list(key_list)

#    def __init__(self,*args, **kwargs):
#        pass
#        #global_variables(request)
class Keywords(BaseContent):
    name = models.CharField(max_length=100, **OPTIONAL)

    def __unicode__(self):
        return self.name or ''
# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
class FileKeywords(BaseContent):
    key = models.ForeignKey(Keywords, **OPTIONAL)
    order_no = models.IntegerField(default=0)
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s",**OPTIONAL)
    object_id = models.IntegerField(**OPTIONAL)

    def __unicode__(self):
        return self.key.name or ''

LOCATION_TYPE = ((0, 'Urban'), (1, 'Semi-urban'), (2, 'Rural'))
# 
class ProjectLocation(BaseContent):
    # 
    location = models.ForeignKey("projectmanagement.Boundary", **OPTIONAL)
    created_by = models.ForeignKey('projectmanagement.UserProfile', **OPTIONAL)
    area = models.CharField(max_length=200, **OPTIONAL)
    ward_no = models.CharField(max_length=50, **OPTIONAL)
    pin_code = models.CharField(max_length=50, **OPTIONAL)
    program_type = models.IntegerField(choices = LOCATION_TYPE, default=0)
    content_type = models.ForeignKey(ContentType,null=True,blank=True, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s")
    object_id = models.IntegerField(_('object ID'),null=True,blank=True)
    relatedTo = GenericForeignKey(ct_field="content_type", fk_field="object_id")

    def __unicode__(self):
        return str(self.id)
# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
class Comment(BaseContent):
    text = models.TextField(**OPTIONAL)
    created_by = models.ForeignKey(
        UserProfile, related_name='comment_created_user', **OPTIONAL)
    content_type = models.ForeignKey(ContentType,null=True,blank=True, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s")
    object_id = models.IntegerField(_('object ID'),null=True,blank=True)
    relatedTo = GenericForeignKey(ct_field="content_type", fk_field="object_id")
# 
class Article(BaseContent):
    name = models.CharField("Name", max_length=300, **OPTIONAL)
    description = models.TextField(**OPTIONAL)
    listing_order = models.IntegerField(default=0, **OPTIONAL)
    parent = models.ForeignKey('self', **OPTIONAL)
    slug = models.SlugField(_("Slug"), blank=True)
# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
class Section(BaseContent):
    # 
    name = models.CharField("Name", max_length=300, **OPTIONAL)
    description = RichTextField(**OPTIONAL)
    summary = RichTextField(**OPTIONAL)
    article = models.ForeignKey('Article', **OPTIONAL)
    cover_image = ImageWithThumbsField(upload_to='static/%Y/%m/%d', sizes=((90,120),(360,480)),blank=True,null=True,help_text="Image size should be 930x300 pixels")
    image = ImageWithThumbsField(upload_to='static/%Y/%m/%d', sizes=((90,120),(360,480)),blank=True,null=True,help_text="Image size should be 930x300 pixels")
    listing_order = models.IntegerField(default=0, blank=True, null=True)
    slug = models.SlugField(_("Slug"), blank=True)
# 
class ContactPersonInformation(BaseContent):
    name = models.CharField("Name", max_length=300, **OPTIONAL)
    email = models.CharField("Email", max_length=500, **OPTIONAL)
    organization_name = models.CharField("Organization Name", max_length=600, **OPTIONAL)
    mobile_number = models.CharField("Mobile Number", max_length=50, **OPTIONAL)
    message = models.TextField(**OPTIONAL)
# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
IMAGE_TYPE = ((1,'Pie-Image'),(2,'Gatt-image'),)
class ScreenshotMedia(BaseContent):

    report_parameter = models.ForeignKey(ReportParameter,**OPTIONAL)
    attachment_file = models.FileField(upload_to='static/%Y/%m/%d', **OPTIONAL)
    img_file_path = models.CharField(max_length = 300,**OPTIONAL)
    content_type = models.ForeignKey(ContentType,null=True,blank=True, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s")
    object_id = models.IntegerField(_('object ID'),null=True,blank=True)
    relatedTo = GenericForeignKey(ct_field="content_type", fk_field="object_id")

    def __unicode__(self):
        return str(self.id) or ''
# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
class Note(BaseContent):
    project = models.ForeignKey("projectmanagement.Project", **OPTIONAL)
    created_by = models.ForeignKey(UserProfile, related_name='note_created_user', **OPTIONAL)
    attachment_file = PrivateFileField(upload_to=get_file_path,max_length=500, **OPTIONAL)    
    description = models.CharField("Description", max_length=600, **OPTIONAL)
    comment = RichTextField(**OPTIONAL)
    history = HistoricalRecords()

    def __unicode__(self):
        return str(self.id)

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
