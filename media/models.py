from django.db import models
from django.contrib import admin
from constants import OPTIONAL
from thumbs import ImageWithThumbsField
from django.views import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from projectmanagement.models import (BaseContent,UserProfile)

ATTACHMENT_TYPE = ((1,'Image'),(2,'Documents'),)
DOCUMENT_TYPE = ((1,'Excel'),(2,'PDF'),(3,'PPT'),(4,'Word Document'))

class Attachment(BaseContent):
    # model to attach files.
    #content_type is a foriegn key, verbose_name- is a function differing with _"
    created_by = models.ForeignKey(
        UserProfile, related_name='document_created_user', **OPTIONAL)
    attachment_file = models.FileField(upload_to='static/%Y/%m/%d', **OPTIONAL)
    name = models.CharField("Description", max_length=300, **OPTIONAL)
    description = models.CharField("Description", max_length=600, **OPTIONAL)
    attachment_type = models.IntegerField('ATTACHMENT_TYPE',choices=ATTACHMENT_TYPE,**OPTIONAL)
    document_type = models.IntegerField('DOCUMENT_TYPE',choices = DOCUMENT_TYPE,**OPTIONAL)
    date = models.DateTimeField(**OPTIONAL)
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s",**OPTIONAL)
    object_id = models.IntegerField(_('object ID'),**OPTIONAL)
    relatedTo = GenericForeignKey(ct_field="content_type", fk_field="object_id")
    URL = models.URLField("Link url", max_length=200, blank=True)
    parent = models.ForeignKey('self', blank=True, null=True)

    def __unicode__(self):
        return str(self.id) or self.object_id

    def get_sub_documents(self):
        try:
            subdocuments = Attachment.objects.filter(active=2,parent=self)
            documents = [{'name':i.name,'file':PHOTO_URL+'/'+i.organisationdocument.document.url} for i in subdocuments]
        except:
            documents = []
        return documents

class Keywords(BaseContent):
    name = models.CharField(max_length=100, **OPTIONAL)

    def __unicode__(self):
        return self.name or ''

class FileKeywords(BaseContent):
    key = models.ForeignKey(Keywords, **OPTIONAL)
    order_no = models.IntegerField(default=0)
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s",**OPTIONAL)
    object_id = models.IntegerField(**OPTIONAL)

    def __unicode__(self):
        return self.key.name or ''

LOCATION_TYPE = ((0, 'Urban'), (1, 'Semi-urban'), (2, 'Rural'))

class ProjectLocation(BaseContent):

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

