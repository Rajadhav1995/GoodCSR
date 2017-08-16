from django.db import models
from .manager import ActiveQuerySet
from django.template.defaultfilters import slugify
from constants import levels, OPTIONAL
import six
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from simple_history.models import HistoricalRecords
from thumbs import ImageWithThumbsField
from simple_history.admin import SimpleHistoryAdmin
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User

#----------------------introduction------------------------------------------#
# Project Management is the application where database tables are related to project
#--------------------ends here--------------------------------------------------#


class BaseContentBase(models.base.ModelBase):

    def __iter__(self):
        return self.objects.all().__iter__()

    @staticmethod
    def register(mdl):
        if (not hasattr(mdl, 'Meta')) or getattr(
                getattr(mdl, '_meta', None),
                'abstract', True
        ):
            return mdl

        class MdlAdmin(admin.ModelAdmin):
            list_display = ['__str__'] + getattr(mdl, 'admin_method', []) + [i.name for i in mdl._meta.fields]
            filter_horizontal = [i.name for i in mdl._meta.many_to_many]

        if hasattr(mdl, 'Admin'):
            class NewMdlAdmin(mdl.Admin, MdlAdmin):
                pass
            admin.site.register(mdl, NewMdlAdmin)

        else:
            admin.site.register(mdl, MdlAdmin)

    def __new__(cls, name, bases, attrs):
        mdl = super(BaseContentBase, cls).__new__(cls, name, bases, attrs)
        BaseContentBase.register(mdl)
        return mdl


class BaseContent(six.with_metaclass(BaseContentBase, models.Model)):
    # ---------comments-----------------------------------------------------#
    # BaseContent is the abstract base model for all
    # the models in the project
    # This contains created and modified to track the
    # history of a row in any table
    # This also contains switch method to deactivate one row if it is active
    # and vice versa
    # ------------------------ends here---------------------------------------------#

    ACTIVE_CHOICES = ((0, 'Inactive'), (2, 'Active'),)
    active = models.PositiveIntegerField(choices=ACTIVE_CHOICES,
                                         default=2)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    Admin = SimpleHistoryAdmin
    objects = ActiveQuerySet.as_manager()
    history = HistoricalRecords()

    #                                        BaseContent
    class Meta:
        #-----------------------------------------#
        # Don't create a table in database
        # This table is abstract
        #--------------------ends here--------------------#
        abstract = True

    #                                        BaseContent
    def switch(self):
        # Deactivate a model if it is active
        # Activate a model if it is inactive
        self.active = {2: 0, 0: 2}[self.active]
        self.save()

    #                                        BaseContent
    def copy(self, commit=True):
        # Create a copy of given item and save in database
        obj = self
        obj.pk = None
        if commit:
            obj.save()
        return obj

    #                                        BaseContent
    def __unicode__(self):
        for i in ['name', 'text']:
            if hasattr(self, i):
                return getattr(self, i, 'Un%sed' % i)
        if hasattr(self, '__str__'):
            return self.__str__()
        return super(BaseContent, self).__unicode__()

class Boundary(BaseContent):
    name = models.CharField(max_length=200,**OPTIONAL)
    boundary_level = models.IntegerField(default=0)
    slug = models.SlugField('Slug', max_length=255, blank=True, null=True)
    parent = models.ForeignKey('self', blank=True, null=True)

    def __str__(self):
        return str(self.id)

class MasterCategory(BaseContent):
    name = models.CharField(max_length=200,**OPTIONAL)
    code = models.CharField(max_length=100,**OPTIONAL)
    slug = models.SlugField('Slug', max_length=255, blank=True, null=True)
    parent = models.ForeignKey('self', **OPTIONAL)

    def __str__(self):
        return str(self.id)

class UserProfile(BaseContent):
    user_reference_id = models.IntegerField(default=0)
    user = models.ForeignKey("auth.User",**OPTIONAL)
    email = models.CharField(max_length=500,**OPTIONAL)
    orgnaization = models.CharField(max_length=800,**OPTIONAL)
    organization_type = models.IntegerField(default=0)
    owner = models.BooleanField(default=False)
    is_admin_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

class Program(BaseContent):
    name = models.CharField(max_length=200,**OPTIONAL)
    start_date = models.DateField(**OPTIONAL)
    end_date = models.DateField(**OPTIONAL)
    created_by = models.ForeignKey(UserProfile,related_name ='program_created_user',**OPTIONAL)
    description = models.TextField('About Project', **OPTIONAL)

    def __str__(self):
        return str(self.id)

REQUEST_STATUS = ((0,''),(1, 'Requested'), (2, 'Request more information'), (3, 'Reject'), (4,'Approved'), (5, 'ShortList'), (6, 'Decision Pending'))
STATUS_CHOICES = ((0,''),(1, 'Open'), (2, 'Close'), (3, 'Ongoing'),)
BUDGET_TYPE = ((1,'Yearly'),(2,'Quarterly'),(3,'Half Yearly'))

class Project(BaseContent):
    program = models.ForeignKey(Program,**OPTIONAL)
    request_status = models.IntegerField(choices=REQUEST_STATUS,default=0)
    name = models.CharField(max_length=200,**OPTIONAL)
    start_date = models.DateField(**OPTIONAL)
    end_date = models.DateField(**OPTIONAL)
    total_budget = models.IntegerField(default=0)
    budget_type = models.IntegerField(choices=BUDGET_TYPE, default=2)
    created_by = models.ForeignKey(UserProfile,related_name ='created_user',**OPTIONAL)
    project_status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    duration = models.IntegerField(default=0)
    summary = RichTextField(**OPTIONAL)
    no_of_beneficiaries = models.IntegerField(default=0)
    cause_area = models.ManyToManyField(MasterCategory,blank=True,related_name="area_category")
    target_beneficiaries = models.ManyToManyField(MasterCategory,blank=True,related_name="target_beneficiaries")
    slug = models.SlugField(_("Slug"), blank=True)
    location = models.ManyToManyField(Boundary,related_name ='project_location',blank=True)
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s")
    object_id = models.IntegerField(_('object ID'))
    relatedTo = generic.GenericForeignKey(ct_field="content_type", fk_field="object_id")
    history = HistoricalRecords()

    def __str__(self):
        return str(self.id)

ACTIVITY_CHOICES = ((0, 'Primary Activities'), (1, 'Scope of work'))

class PrimaryWork(BaseContent):
    types = models.IntegerField(choices=ACTIVITY_CHOICES, **OPTIONAL)
    name = models.TextField(blank=True, null=True)
    number = models.IntegerField(default=0)
    activity_duration = models.IntegerField(default=0)
    content_type = models.ForeignKey(ContentType,null=True,blank=True, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s")
    object_id = models.IntegerField(_('object ID'),null=True,blank=True)
    relatedTo = generic.GenericForeignKey(ct_field="content_type", fk_field="object_id")

    def __str__(self):
        return str(self.id)

class ProjectFunderRelation(BaseContent):
    project = models.ForeignKey(Project,**OPTIONAL)
    funder = models.ForeignKey(UserProfile,related_name="funder")
    implementation_partner = models.ForeignKey(UserProfile,related_name="implementation_partner")
    total_budget = models.IntegerField(default=0)


class KeyParameter(BaseContent):
    name = models.CharField(max_length=300,**OPTIONAL)
    parameter_type = models.ForeignKey(MasterCategory,**OPTIONAL)
    project = models.ForeignKey(Project,**OPTIONAL)

class keyParameterValue(BaseContent):
    keyparameter = models.ForeignKey(KeyParameter)
    name = models.CharField(max_length=300,**OPTIONAL)
    date = models.DateField(**OPTIONAL)
    parameter_value = models.CharField(max_length=300,**OPTIONAL)
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s")
    object_id = models.IntegerField(_('object ID'))

class ProjectUserRoleRelationship(BaseContent):
    project = models.ForeignKey(Project,**OPTIONAL)
    user = models.ForeignKey(UserProfile,**OPTIONAL)
    role = models.CharField(max_length=300,**OPTIONAL)
    history = HistoricalRecords()

