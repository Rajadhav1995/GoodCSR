import re
from collections import OrderedDict
from django import forms
from django.contrib.auth.models import User
from django.contrib.admin import widgets
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.fields import RichTextUploadingField
from django.core.validators import *
from django.core.exceptions import ValidationError
from django.contrib.admin.widgets import FilteredSelectMultiple
from taskmanagement.models import *
from budgetmanagement.models import *
from projectmanagement.models import UserProfile,Project
from userprofile.models import (ProjectUserRoleRelationship,)


ACTIVITY_CHOICES = ((1,'Core'),(2,'Non-core'),)
STATUS_CHOICES = ((0,' '),(1, 'Open'), (2, 'Close'), (3, 'Ongoing'),)
MILESTONE_CHOICES=((0,' '),(1, 'Open'), (3, 'Ongoing'),)

class ActivityForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True,max_length=200)
    project = forms.ModelChoiceField(queryset = Project.objects.filter(active=2),required=True,widget=forms.Select(attrs={'class': 'form-control'}),label='')
    activity_type = forms.ChoiceField(choices = ACTIVITY_CHOICES,widget = forms.Select(attrs={'class': 'form-control'}),required=False)
    super_category = forms.ModelChoiceField(queryset= SuperCategory.objects.filter(active = 2).exclude(parent = None),required=False, widget = forms.Select(attrs={'class': 'form-control'}))
    status = forms.ChoiceField(choices = STATUS_CHOICES,widget = forms.Select(attrs={'class': 'form-control'}),required=True)
    assigned_to = forms.ModelChoiceField(queryset = UserProfile.objects.filter(active=2),required=True,widget=forms.Select(attrs={'class': 'form-control'}))
    subscribers = forms.ModelMultipleChoiceField(queryset = UserProfile.objects.filter(active=2),required=False,widget = forms.SelectMultiple(attrs = {'class': 'test'}))
    description = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control text_area'}), required=False,max_length=200)
    class Meta:
        model = Activity
        fields  = ('name','super_category','activity_type','description','status','assigned_to','subscribers','project')

    def __init__(self,user_id,project_id,*args, **kwargs):
        self.user = user_id
        self.project = project_id
        super(ActivityForm, self).__init__(*args, **kwargs)
        self.fields['description'].required = True
        self.fields['name'].required = True
        self.fields['activity_type'].required = True
        self.fields['status'].initial = 1
        self.fields['assigned_to'].required = True
        self.fields['project'].initial = Project.objects.get(id = int(project_id))
        self.fields['project'].widget = forms.HiddenInput()
        self.fields['super_category'].queryset = SuperCategory.objects.filter(active=2,project__id=project_id).exclude(parent = None)
        self.fields['assigned_to'].queryset = UserProfile.objects.filter(active=2)
    def clean(self):
        cleaned_data = super(ActivityForm,self).clean()
        super_category= cleaned_data.get("super_category")
        
        if not super_category:
            msg = u"Please select super category"
            self._errors["super_category"] = self.error_class([msg])

class TaskForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True,max_length=200)
    super_category = forms.ModelMultipleChoiceField(queryset= SuperCategory.objects.filter(active = 2).exclude(parent = None),required=False, widget = forms.SelectMultiple(attrs = {'class': 'test'}))
    activity = forms.ModelChoiceField(queryset= Activity.objects.filter(active = 2),required=True, widget = forms.Select(attrs={'class': 'form-control'}))
    task_dependency = forms.ModelMultipleChoiceField(queryset = Task.objects.filter(active=2),required=False,widget = forms.SelectMultiple(attrs = {'class': 'test'}))
    start_date = forms.DateTimeField(widget=forms.TextInput(attrs={'class':'form-control','readonly':'true'}), required=True)
    end_date = forms.DateTimeField(widget=forms.TextInput(attrs={'class':'form-control','readonly':'true'}), required=True)
    actual_start_date = forms.DateTimeField(widget=forms.TextInput(attrs={'class':'form-control','readonly':'true'}), required=False)
    actual_end_date = forms.DateTimeField(widget=forms.TextInput(attrs={'class':'form-control','readonly':'true'}), required=False)
    status = forms.ChoiceField(choices = STATUS_CHOICES,widget = forms.Select(attrs={'class': 'form-control'}),required=True)
    assigned_to = forms.ModelChoiceField(queryset = UserProfile.objects.filter(active=2),required=True,widget=forms.Select(attrs={'class': 'form-control'}))
    subscribers = forms.ModelMultipleChoiceField(queryset = UserProfile.objects.filter(active=2),required=False,widget = forms.SelectMultiple(attrs = {'class': 'test'}))
    
    class Meta:
        model = Task
        fields = ('name','activity','task_dependency','start_date','end_date','actual_start_date','actual_end_date','assigned_to','subscribers','status')

    def __init__(self,user_id ,project_id,*args, **kwargs):
        self.user = user_id
        self.project = project_id
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['activity'].queryset = Activity.objects.filter(project_id = project_id)
        self.fields['name'].required = True
        self.fields['status'].initial = 1
        self.fields['assigned_to'].required = True
        self.fields['task_dependency'].queryset = Task.objects.filter(active=2,activity__project__id=project_id)
        self.fields['super_category'].queryset = SuperCategory.objects.filter(active=2,project__id=project_id).exclude(parent = None)
        self.fields['assigned_to'].queryset = UserProfile.objects.filter(active=2)
        self.fields = OrderedDict([
            ('name',self.fields['name']),
            ('super_category',self.fields['super_category']),
            ('activity',self.fields['activity']),
            ('task_dependency',self.fields['task_dependency']),
            ('start_date',self.fields['start_date']),
            ('end_date',self.fields['end_date']),
            ('actual_start_date',self.fields['actual_start_date']),
            ('actual_end_date',self.fields['actual_end_date']),
            ('assigned_to',self.fields['assigned_to']),
            ('subscribers',self.fields['subscribers']),
            ('status',self.fields['status']),
            ])
    
    def clean(self):
        cleaned_data = super(TaskForm,self).clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        actual_start_date = cleaned_data.get("actual_start_date")
        actual_end_date = cleaned_data.get("actual_end_date")
        
        if start_date and end_date == '' :
            msg = u"Please enter the end date"
            self._errors["end_date"] = self.error_class([msg])
        if start_date and end_date and end_date < start_date:
            msg = u"End date should be greater than start date."
            self._errors["end_date"] = self.error_class([msg])

        if actual_end_date and actual_start_date and actual_end_date < actual_start_date:
            msg = u"Actual End date should be greater than Actual start date."
            self._errors["actual_end_date"] = self.error_class([msg])

class MilestoneForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True,max_length=200)
    super_category = forms.ModelMultipleChoiceField(queryset= SuperCategory.objects.filter(active = 2).exclude(parent = None),required=False, widget = forms.SelectMultiple(attrs = {'class': 'test'}))
    activity =forms.ModelMultipleChoiceField(queryset= Activity.objects.filter(active = 2),required=True, widget = forms.SelectMultiple(attrs = {'class': 'test'}))
    task = forms.ModelMultipleChoiceField(queryset= Task.objects.filter(active = 2),required=False, widget = forms.SelectMultiple(attrs={'class' :'test'}))
    status = forms.ChoiceField(choices = MILESTONE_CHOICES,widget = forms.Select(attrs={'class': 'form-control'}),required=True)
    subscribers  =forms.ModelMultipleChoiceField(queryset = UserProfile.objects.filter(active=2),required=False,widget = forms.SelectMultiple(attrs = {'class': 'test'}))
    overdue = forms.DateTimeField(widget=forms.TextInput(attrs={'class':'form-control','readonly':'true'}), required=False)
    project = forms.ModelChoiceField(queryset = Project.objects.filter(active=2),required=True,widget=forms.Select(attrs={'class': 'form-control'}),label='')
    class Meta:
        model = Milestone
        fields = ('name','task','overdue','subscribers','status','project')


    def __init__(self,user_id,project_id,*args, **kwargs):
        self.user = user_id
        self.project = project_id
        super(MilestoneForm, self).__init__(*args, **kwargs)
        self.fields['project'].initial = Project.objects.get(id=int(project_id))
        self.fields['name'].required = True
        self.fields['overdue'].required = False
        self.fields['task'].queryset = Task.objects.filter(active=2,activity__project_id=project_id)
        self.fields['status'].initial = 1
        self.fields['project'].widget = forms.HiddenInput()
        self.fields['task'].required = True
        self.fields['super_category'].queryset = SuperCategory.objects.filter(active=2,project__id=project_id).exclude(parent = None)
        self.fields['activity'].queryset = Activity.objects.filter(project_id = project_id)
        self.fields = OrderedDict([
            ('name',self.fields['name']),
            ('super_category',self.fields['super_category']),
            ('activity',self.fields['activity']),
            ('task',self.fields['task']),
            ('overdue',self.fields['overdue']),
            ('subscribers',self.fields['subscribers']),
            ('status',self.fields['status']),
            ('project',self.fields['project'])
            ])
        
