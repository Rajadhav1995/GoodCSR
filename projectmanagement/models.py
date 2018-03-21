from django.db import models
from jsonfield import JSONField
from django.db.models import Sum
from .manager import ActiveQuerySet
from django.utils.encoding import smart_str, smart_unicode
from django.template.defaultfilters import slugify
from constants import levels, OPTIONAL
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
from django.template.defaultfilters import slugify
import datetime

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
    modified_by = models.CharField(max_length=50,blank=True, null=True)
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


CATEGORY_CHOICES=(('DBC', 'Direct to Beneficiary Cost'),
    ('IC', 'Indirect Cost'), 
    ('AC', 'Admin Cost'), 
     ('O', 'Others')) 

class MasterCategory(BaseContent):
    #this model structure is to store categories 
    category_type = models.CharField(choices=CATEGORY_CHOICES,max_length=100,blank=True, null=True)
    name = models.CharField(max_length=200,**OPTIONAL)
    code = models.CharField(max_length=100,**OPTIONAL)
    slug = models.SlugField('Slug', max_length=255, blank=True, null=True)
    parent = models.ForeignKey('self', **OPTIONAL)

    def __str__(self):
        return str(self.id)

def my_default():
    return {'first_name': '','last_name':''}

class UserProfile(BaseContent):
    #this model structure is to store user details
    user_reference_id = models.IntegerField(default=0)
    user = models.ForeignKey("auth.User",**OPTIONAL)
    name = models.CharField(max_length=500,**OPTIONAL)
    designation = models.CharField(max_length=200,**OPTIONAL)
    email = models.CharField(max_length=500,**OPTIONAL)
    organization = models.CharField(max_length=800,**OPTIONAL)
    organization_type = models.IntegerField(default=0)
    owner = models.BooleanField(default=False)
    is_admin_user = models.BooleanField(default=False)
    attrs = JSONField(default=my_default)

    def __unicode__(self):
        return str(self.email) or ''

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
    #this model structure is to store detail information about Project and its related data
    program = models.ForeignKey(Program,**OPTIONAL)
    request_status = models.IntegerField(choices=REQUEST_STATUS,default=0)
    name = models.CharField(max_length=300,**OPTIONAL)
    start_date = models.DateField(**OPTIONAL)
    end_date = models.DateField(**OPTIONAL)
    total_budget = models.IntegerField(default=0)
    budget_type = models.IntegerField(choices=BUDGET_TYPE, default=2)
    created_by = models.ForeignKey(UserProfile,related_name ='created_user',**OPTIONAL)
    project_status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    duration = models.IntegerField(default=0)
    summary = RichTextField(**OPTIONAL)
    program_aim = RichTextField(**OPTIONAL)
    no_of_beneficiaries = models.IntegerField(default=0)
    cause_area = models.ManyToManyField(MasterCategory,blank=True,related_name="area_category")
    target_beneficiaries = models.ManyToManyField(MasterCategory,blank=True,related_name="target_beneficiaries")
    slug = models.SlugField(_("Slug"), max_length=300,blank=True)
    location = models.ManyToManyField(Boundary,related_name ='project_location',blank=True)
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s")
    object_id = models.IntegerField(_('object ID'))
    relatedTo = GenericForeignKey(ct_field="content_type", fk_field="object_id")
    history = HistoricalRecords()

    def __str__(self):
        return smart_str(self.name) or ''

    def total_tasks(self):
        # this model method is for total task count for project
        from taskmanagement.models import Activity,Task
        project = Project.objects.get(id= self.id)
        activity = Activity.objects.filter(project = project)
        task_count = Task.objects.filter(activity__project= project).count()
        return task_count
        
    def tasks_completed(self):
        # this model method is for total completed task count for project
        from taskmanagement.models import Activity,Task
        from datetime import datetime
        completed_tasks = 0
        project = Project.objects.get(id= self.id)
        activity = Activity.objects.filter(project = project)
        task_list = Task.objects.filter(activity__project= project)
        for task in task_list:
            if task.status == 2:
                completed_tasks = completed_tasks + 1
        return completed_tasks

    def project_budget_details(self):
        from budgetmanagement.models import (Budget,ProjectBudgetPeriodConf,
                                            Tranche,BudgetPeriodUnit)
        budgetobj = Budget.objects.latest_one(project = self)
        budget_periodlist = ProjectBudgetPeriodConf.objects.filter(project = self,budget = budgetobj,active=2).values_list('id', flat=True)
        budget_periodunitlist = BudgetPeriodUnit.objects.filter(budget_period__id__in=budget_periodlist,active=2)
        planned_cost = budget_periodunitlist.aggregate(Sum('planned_unit_cost')).values()[0]
        utilized_cost = budget_periodunitlist.aggregate(Sum('utilized_unit_cost')).values()[0]
        disbursed_cost = Tranche.objects.filter(project = self,active=2).aggregate(Sum('actual_disbursed_amount')).values()[0] or 0
        total_percent = 100
        try:
            disbursed_percent = int((disbursed_cost/planned_cost)*100) if disbursed_cost else 0
            utilized_percent = int((utilized_cost/planned_cost)*100) if utilized_cost else 0 
        except:
            disbursed_percent = 0
            utilized_percent = 0
        project_budget = {'planned_cost':int(planned_cost) if planned_cost else 0,
                          'utilized_cost':int(utilized_cost) if utilized_cost else 0,
                          'disbursed_cost':int(disbursed_cost) if disbursed_cost else 0,
                          'disbursed_percent':disbursed_percent,
                          'utilized_percent':utilized_percent,
                          }
        return project_budget

    # def save(self):
    #     super(Project, self).save()
    #     date = datetime.date.today()
    #     self.slug = '%i-%s' % (
    #         date.day, slugify(self.name)
    #     )
    #     super(Project, self).save()'
    
    def get_todays_tasks(self,today,user,status):
        from taskmanagement.models import Task
        if status == '1':
            tasks = Task.objects.filter(activity__project__id = self.id,active=2,start_date = today).order_by('-id')
        else:   
            tasks = Task.objects.filter(activity__project__id = self.id,active=2,start_date = today,assigned_to=user).order_by('-id')
        return tasks

    def get_remaining_tasks(self,remain_days,user,status):

        from taskmanagement.models import Task
        if status == '1':
            tasks = Task.objects.filter(activity__project__id = self.id,active=2,start_date__gte = remain_days).order_by('-id')
        else:
            tasks = Task.objects.filter(activity__project__id = self.id,active=2,start_date__gte = remain_days,assigned_to=user).order_by('-id')
        return tasks
        
    
    def get_locations(self):
        from media.models import ProjectLocation
        project = Project.objects.get_or_none(id=self.id)
        locations = ProjectLocation.objects.filter(active=2,content_type= ContentType.objects.get_for_model(project),object_id=project.id)
        loc_list = [i.location.name+'-'+i.location.parent.name+'-'+i.get_program_type_display() for i in locations] if locations else []
        loc = ','.join(loc_list)
        return loc
        
        
ACTIVITY_CHOICES = ((0, 'Primary Activities'), (1, 'Scope of work'))

class PrimaryWork(BaseContent):
    types = models.IntegerField(choices=ACTIVITY_CHOICES, **OPTIONAL)
    name = models.TextField(blank=True, null=True)
    number = models.IntegerField(default=0)
    activity_duration = models.IntegerField(default=0)
    content_type = models.ForeignKey(ContentType,null=True,blank=True, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s")
    object_id = models.IntegerField(_('object ID'),null=True,blank=True)
    relatedTo = GenericForeignKey(ct_field="content_type", fk_field="object_id")

    def __str__(self):
        return str(self.id)

class ProjectFunderRelation(BaseContent):
    project = models.ForeignKey(Project,**OPTIONAL)
    funder = models.ForeignKey(UserProfile,related_name="funder")
    implementation_partner = models.ForeignKey(UserProfile,related_name="implementation_partner")
    total_budget = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)


''' Jagpreet Made these changes for Project parameters, Start:
'''

AGGREGATION_FUNCTION_CHOICES=(('ADD', 'ADDITION'), # Simple Addition 
    ('AVG', 'AVERAGE'), # Average over the time period
    ('WAV', 'Weighted Average'), # Weighted average along with another field 
     ('WAP', 'Weighted average over peers')) # Weighted average for all sections of a pie chart

PARAMETER_TYPE_CHOICES=(('PIN','Pie chart Numbers'),
                          ('PIP', 'Pie Chart Percent'),
                          ('NUM','Number'),
                          ('PER','Percent'),
                          ('CUR','Currency'))

class ProjectParameter(BaseContent):
    parameter_type = models.TextField(choices=PARAMETER_TYPE_CHOICES,default='NUM',)
    project = models.ForeignKey(Project, **OPTIONAL)
    name = models.CharField(max_length=300, **OPTIONAL)
    aggregation_function = models.TextField(choices=AGGREGATION_FUNCTION_CHOICES, default='ADD')
    parent = models.ForeignKey('self', **OPTIONAL)
    instructions=models.CharField(max_length=300, **OPTIONAL) # Instructions shown when reporting parameter
    history = HistoricalRecords()
    
    def __str__(self):
        return str(self.id)


class ProjectParameterValue(BaseContent):
    keyparameter = models.ForeignKey(ProjectParameter)
    submit_date = models.DateField(**OPTIONAL)
    parameter_value = models.CharField(max_length=300)
    start_date = models.DateField(**OPTIONAL) # Period for paramter, typically month start
    end_date = models.DateField(**OPTIONAL)  # Period  for paramter, typically month end
    comment = models.CharField(max_length=300, **OPTIONAL)
    has_attachment = models.BooleanField(default=False) # True if the parameter has a supporting attachment

    def __str__(self):
        return str(self.id)

'''Jagpreet Made these changes for Project parameters, END;
'''
