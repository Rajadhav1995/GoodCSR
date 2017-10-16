import six
from django.contrib import admin
from django.db import models
from constants import  OPTIONAL
from django.template.defaultfilters import slugify
from django.views import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.auth.models import User
from thumbs import ImageWithThumbsField
from simple_history.models import HistoricalRecords
from simple_history.admin import SimpleHistoryAdmin
from ckeditor.fields import RichTextField
from projectmanagement.models import BaseContent
from projectmanagement.manager import ActiveQuerySet

#----------------------introduction------------------------------------------#
# Budget Management is the application where database tables are related to Budget,Budget Category
#--------------------ends here--------------------------------------------------#
# HistoricalRecords to keep track of the object creation/modification
BUDGET_TYPE = ((1,'Yearly'),(2,'Quarterly'),(3,'Half Yearly'))
BUDGET_STATUS = ((0,''),(1, 'Requested'), (2, 'Request more information'), (3, 'Reject'), (4,'Approved'),)

class Budget(BaseContent):
    project = models.ForeignKey('projectmanagement.Project')
    status = models.IntegerField(choices=BUDGET_STATUS,default=0)
    name = models.CharField(max_length=100,**OPTIONAL)
    start_date = models.DateField(**OPTIONAL)
    actual_start_date = models.DateField(**OPTIONAL)
    end_date = models.DateField(**OPTIONAL)
    financial_type = models.IntegerField(choices=BUDGET_TYPE, default=2)
    history = HistoricalRecords()

    def __str__(self):
        return str(self.id) if self.id else str(0)

class SuperCategory(BaseContent):
    budget = models.ForeignKey(Budget,**OPTIONAL)
    name = models.CharField(max_length=200,**OPTIONAL)
    slug = models.SlugField(_("Slug"), blank=True)
    description = models.TextField(**OPTIONAL)
    parent = models.ForeignKey('self',**OPTIONAL)
    project = models.ForeignKey('projectmanagement.Project',**OPTIONAL)
    history = HistoricalRecords()

    def __str__(self):
        return str(self.id) if self.id else str(0)

class ProjectBudgetPeriodConf(BaseContent):
    budget = models.ForeignKey(Budget,**OPTIONAL)
    name = models.CharField(max_length=300,**OPTIONAL)
    project = models.ForeignKey('projectmanagement.Project')
    start_date = models.DateField(**OPTIONAL)
    end_date = models.DateField(**OPTIONAL)
    row_order = models.IntegerField(default=0)
    history = HistoricalRecords()

    def __str__(self):
        return str(self.id)

# Planned amount is ngo expected amount,actual_disbursed_amount is corporate released amount,
# recommended_amount is amount recommended by samhita,utilized_amount is the actual utilized_amount for one quarter
class Tranche(BaseContent):
    budget_period = models.ForeignKey(ProjectBudgetPeriodConf,**OPTIONAL)
    project = models.ForeignKey('projectmanagement.Project',**OPTIONAL)
    name = models.CharField(max_length = 200, **OPTIONAL)
    planned_amount = models.IntegerField(default=0)
    actual_disbursed_amount = models.IntegerField(default=0)
    recommended_amount = models.IntegerField(default=0)
    recommended_by = models.ForeignKey("projectmanagement.UserProfile",**OPTIONAL)
    utilized_amount = models.IntegerField(default=0)
    due_date = models.DateField(**OPTIONAL)
    disbursed_date = models.DateField(**OPTIONAL)
    history = HistoricalRecords()

EXPENSES_TYPE = ((1,'Programmatic'),(2,'Non-programmatic'))
class BudgetPeriodUnit(BaseContent):
# ----to set budget period
    created_by = models.ForeignKey("projectmanagement.UserProfile",**OPTIONAL)
    expenses_type = models.IntegerField(choices=EXPENSES_TYPE,**OPTIONAL)
    budget_period = models.ForeignKey(ProjectBudgetPeriodConf,**OPTIONAL)
    category = models.ForeignKey(SuperCategory,**OPTIONAL)
    heading = models.ForeignKey('projectmanagement.MasterCategory',**OPTIONAL)
    subheading = models.CharField(max_length=200,**OPTIONAL)
    unit = models.CharField(max_length=200,**OPTIONAL)
    unit_type = models.CharField(max_length=200,**OPTIONAL)
    rate = models.CharField(max_length=200,**OPTIONAL)
    planned_unit_cost = models.CharField(max_length=200,**OPTIONAL)
    utilized_unit_cost = models.CharField(max_length=200,**OPTIONAL)
    variance = models.CharField(max_length=200,**OPTIONAL)
    start_date = models.DateTimeField(**OPTIONAL)
    end_date = models.DateTimeField(**OPTIONAL)
    remarks = models.TextField()
    row_order = models.IntegerField(default=0)
    quarter_order = models.IntegerField(default=0)
    history = HistoricalRecords()

    def __str__(self):
        return str(self.id)

REPORT_TYPE = ((1,'Quarterly'),(2,'Monthly'))
class ProjectReport(BaseContent):
    project = models.ForeignKey('projectmanagement.Project',**OPTIONAL)
    created_by = models.ForeignKey("projectmanagement.UserProfile",**OPTIONAL)
    report_type = models.IntegerField(choices=REPORT_TYPE,**OPTIONAL)
    name = models.CharField(max_length = 500,**OPTIONAL)
    start_date = models.DateTimeField(**OPTIONAL)
    end_date = models.DateTimeField(**OPTIONAL)
    description = models.TextField()
    objective = models.TextField()

    def __str__(self):
        return str(self.id)

QUARTER_TYPE = ((1,'Previous Quarter Updates'),(2,'Current Quarter Updates'),(3,'Future Quarter Updates'))
class QuarterReportSection(BaseContent):
    project = models.ForeignKey(ProjectReport,**OPTIONAL)
    quarter_type = models.IntegerField(choices=QUARTER_TYPE,**OPTIONAL)
    description = models.TextField(**OPTIONAL)
    budget_utilization = models.TextField(**OPTIONAL)
    about_budget = models.TextField(**OPTIONAL)
    risks_mitigation = models.TextField(**OPTIONAL)
    start_date = models.DateField(**OPTIONAL)
    end_date = models.DateField(**OPTIONAL)
    duration = models.IntegerField(default=0)
    quarter_order = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)

class ReportMilestoneActivity(BaseContent):
    quarter = models.ForeignKey(QuarterReportSection,**OPTIONAL)
    name = models.TextField(**OPTIONAL)
    description = models.TextField(**OPTIONAL)

    def __str__(self):
        return str(self.id)



PARAMETER_TYPE_CHOICES=(('PIN','Pie chart Numbers'),
                          ('PIP', 'Pie Chart Percent'),
                          ('NUM','Number'),
                          ('PER','Percent'),
                          ('CUR','Currency'))
class ReportParameter(BaseContent):
    quarter = models.ForeignKey(QuarterReportSection,**OPTIONAL)
    keyparameter = models.ForeignKey('projectmanagement.ProjectParameter',**OPTIONAL)
    parameter_type = models.TextField(choices=PARAMETER_TYPE_CHOICES,default='NUM',)
    description = models.TextField(**OPTIONAL)

    def __str__(self):
        return str(self.id)

# Survey kind of strucutre
class Survey(BaseContent):
    name = models.CharField(max_length=300,**OPTIONAL)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    order = models.IntegerField(default=0)

class Block(BaseContent):

    BLOCK_TYPE_CHOICES = (
        (0, 'Basic Survey'),
        (1, 'Inline Assessment'),
    )

    survey = models.ForeignKey(Survey,**OPTIONAL)
    name = models.CharField(max_length=300,**OPTIONAL)
    slug = models.SlugField(_("Slug"), blank=True)
    block_type = models.IntegerField(choices = BLOCK_TYPE_CHOICES, default = 0)
    order = models.IntegerField(default=0)
    code = models.CharField(max_length=100,**OPTIONAL)

class Question(BaseContent):

    QTYPE_CHOICES = (
        ('T', 'Text Input'), ('S', 'Select One Choice'), ('R', 'Radio List'),
        ('C', 'Checkbox List'), ('D', 'Date'),('M','Master'),('F','File Field'),
        ('Q','API Question'),('DD','Drop Down'),('OT','Other type'),
        ('MC','Multi-Checkbox'),('ck','CKeditor'),('APT','Auto Populate Text'),('API','Auto Populate Image')
    )
    VALIDATION_CHOICES = (
        (0, 'Digit'), (1, 'Number'), (2, 'Alphabet'),
        (3, 'Alpha Numeric'), (4, 'No Validation'),
    )

    block = models.ForeignKey(Block, verbose_name=_('Blocks'))
    qtype = models.CharField(_('question type'), max_length=10,
                             choices=QTYPE_CHOICES)
    text = models.CharField(max_length=300,**OPTIONAL)
    validation = models.IntegerField(choices=VALIDATION_CHOICES,
                                     blank=True, null=True)
    order = models.IntegerField(default = 0)
    code = models.IntegerField(default = 0)
    help_text = models.TextField(**OPTIONAL)
    slug = models.SlugField(_("Slug"), blank=True)
    parent = models.ForeignKey('self', blank=True, null=True)
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s",**OPTIONAL)
    object_id = models.IntegerField(_('object ID'),**OPTIONAL)
    relatedTo = GenericForeignKey(ct_field="content_type", fk_field="object_id")

class Answer(BaseContent):
    user = models.ForeignKey(
        "projectmanagement.UserProfile", related_name='report_user', **OPTIONAL)
    quarter = models.ForeignKey(QuarterReportSection,**OPTIONAL)
    question = models.ForeignKey(Question,**OPTIONAL)
    text = models.TextField(**OPTIONAL)
    inline_answer = models.CharField(max_length=600,**OPTIONAL) #this is to tag milestone and paramters'id.
    attachment_file = models.FileField(upload_to='static/%Y/%m/%d', **OPTIONAL)
    content_type = models.ForeignKey(ContentType, verbose_name=_('content type'), related_name="content_type_set_for_%(class)s",**OPTIONAL)
    object_id = models.IntegerField(_('object ID'),**OPTIONAL)
    relatedTo = GenericForeignKey(ct_field="content_type", fk_field="object_id")

OPTION_TYPE = ((1,"Question Type"),(2,"Block type"),(3,"invite"))
class RemoveQuestion(BaseContent):
    quarter_report = models.ForeignKey(ProjectReport,**OPTIONAL)
    text = models.TextField(**OPTIONAL) #to tag the removed question or section id's'
    
