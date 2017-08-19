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
# Budget Management is the application where database tables are related to Budget,Budget Category
#--------------------ends here--------------------------------------------------#
# HistoricalRecords to keep track of the object creation/modification

class SuperCategory(BaseContent):
    name = models.CharField(max_length=200,**OPTIONAL)
    slug = models.SlugField(_("Slug"), blank=True)
    description = models.TextField(**OPTIONAL) 
    project = models.ForeignKey('projectmanagement.Project',**OPTIONAL)
    history = HistoricalRecords()

class ProjectBudgetPeriodConf(BaseContent):
    name = models.CharField(max_length=300,**OPTIONAL)
    project = models.ForeignKey('projectmanagement.Project')
    start_date = models.DateField(**OPTIONAL)
    end_date = models.DateField(**OPTIONAL)

EXPENSES_TYPE = ((1,'Programmatic'),(2,'Non-programmatic'))
class BudgetCategory(BaseContent):
#---------to create budget category for budget details
    super_category = models.ForeignKey(SuperCategory)
    heading = models.CharField(max_length=200,**OPTIONAL)
    expenses_type = models.IntegerField(choices=EXPENSES_TYPE,**OPTIONAL)
    order = models.IntegerField(**OPTIONAL)
    parent = models.ForeignKey('self', blank=True, null=True)

# Planned amount is ngo expected amount,actual_disbursed_amount is corporate released amount,
# recommended_amount is amount recommended by samhita,utilized_amount is the actual utilized_amount for one quarter
class Tranche(BaseContent):
    budget_period = models.ForeignKey(ProjectBudgetPeriodConf,**OPTIONAL)
    name = models.CharField(max_length = 200, **OPTIONAL)
    planned_amount = models.IntegerField(default=0)
    actual_disbursed_amount = models.IntegerField(default=0)
    recommended_amount = models.IntegerField(default=0)
    recommended_by = models.ForeignKey("projectmanagement.UserProfile",**OPTIONAL)
    utilized_amount = models.IntegerField(default=0)
    due_date = models.DateField(**OPTIONAL)
    disbursed_date = models.DateField(**OPTIONAL)
    history = HistoricalRecords()

class BudgetPeriodUnit(BaseContent):
# ----to set budget period
    created_by = models.ForeignKey("projectmanagement.UserProfile",**OPTIONAL)
    budget_heading = models.ForeignKey(BudgetCategory,**OPTIONAL)
    budget_period = models.ForeignKey(ProjectBudgetPeriodConf,**OPTIONAL)
    subheading = models.CharField(max_length=200,**OPTIONAL)
    unit = models.CharField(max_length=200,**OPTIONAL)
    unit_type = models.CharField(max_length=200,**OPTIONAL)
    rate = models.CharField(max_length=200,**OPTIONAL)
    planned_unit_cost = models.CharField(max_length=200,**OPTIONAL)
    utilized_unit_cost = models.CharField(max_length=200,**OPTIONAL)
    start_date = models.DateTimeField(**OPTIONAL)
    end_date = models.DateTimeField(**OPTIONAL)
    remarks = models.TextField()
    order = models.IntegerField(default=0)
    history = HistoricalRecords()

