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


ACTIVITY_CHOICES = ((1,'Core'),(2,'Non-core'),)
STATUS_CHOICES = ((0,' '),(1, 'Open'), (2, 'Close'), (3, 'Ongoing'),)

class ActivityForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True,max_length=200)
    project = forms.ModelChoiceField(queryset = Project.objects.filter(active=2),required=True,widget=forms.Select(attrs={'class': 'form-control'}))
    activity_type = forms.ChoiceField(choices = ACTIVITY_CHOICES,widget = forms.Select(attrs={'class': 'form-control'}),required=False)
    super_category = forms.ModelChoiceField(queryset= SuperCategory.objects.filter(active = 2).exclude(parent = None),required=False, widget = forms.Select(attrs={'class': 'form-control'}))
    status = forms.ChoiceField(choices = STATUS_CHOICES,widget = forms.Select(attrs={'class': 'form-control'}),required=True)
    assigned_to = forms.ModelChoiceField(queryset = UserProfile.objects.filter(active=2),required=True,widget=forms.Select(attrs={'class': 'form-control'}))
    subscribers = forms.ModelMultipleChoiceField(queryset = UserProfile.objects.filter(active=2),required=True,widget=forms.SelectMultiple(attrs={'class' :'form-control'}))
    class Meta:
        model = Activity
        fields  = ('name','project','super_category','activity_type','description','status','assigned_to','subscribers')
        
    def __init__(self,user_id,*args, **kwargs):
        self.user = user_id
        super(ActivityForm, self).__init__(*args, **kwargs)
        self.fields['description'].required = True
        self.fields['name'].required = True
        self.fields['activity_type'].required = True
        self.fields['status'].required = True
        self.fields['assigned_to'].queryset = User.objects.filter(id__in = UserProfile.objects.filter(active=2).values_list('id',flat="True")).exclude(id = user_id)
        self.fields['subscribers'].required = True
        self.fields['project'].required = True

class TaskForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True,max_length=200)
    activity = forms.ModelChoiceField(queryset= Activity.objects.filter(active = 2),required=True, widget = forms.Select(attrs={'class': 'form-control'}))
    start_date = forms.DateTimeField(widget=forms.TextInput(attrs={'class':'form-control','readonly':'true'}), required=True)
    end_date = forms.DateTimeField(widget=forms.TextInput(attrs={'class':'form-control','readonly':'true'}), required=True)
    actual_start_date = forms.DateTimeField(widget=forms.TextInput(attrs={'class':'form-control','readonly':'true'}), required=True)
    actual_end_date = forms.DateTimeField(widget=forms.TextInput(attrs={'class':'form-control','readonly':'true'}), required=True)
    status = forms.ChoiceField(choices = STATUS_CHOICES,widget = forms.Select(attrs={'class': 'form-control'}),required=True)
    assigned_to = forms.ModelChoiceField(queryset = UserProfile.objects.filter(active=2),required=True,widget=forms.Select(attrs={'class': 'form-control'}))
    subscribers = forms.ModelMultipleChoiceField(queryset = UserProfile.objects.filter(active=2),required=True,widget=forms.SelectMultiple(attrs={'class' :'form-control'}))
    class Meta:
        model = Task
        fields = ('name','activity','start_date','end_date','actual_start_date','actual_end_date','assigned_to','subscribers','status')
        
    def __init__(self,user_id ,*args, **kwargs):
        self.user = user_id
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['activity'].required = True
        self.fields['name'].required = True
        self.fields['start_date'].required = True
        self.fields['end_date'].required = True
        self.fields['status'].required = True
        

class MilestoneForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True,max_length=200)
    task = forms.ModelMultipleChoiceField(queryset= Task.objects.filter(active = 2),required=True, widget = forms.Select(attrs={'class': 'form-control'}))
    status = forms.ChoiceField(choices = STATUS_CHOICES,widget = forms.Select(attrs={'class': 'form-control'}),required=True)
    subscribers  =forms.ModelMultipleChoiceField(queryset = UserProfile.objects.filter(active=2),required=True,widget=forms.SelectMultiple(attrs={'class' :'form-control'})) 
#    overdue = forms.DateField(widget=forms.TextInput(attrs={'class':'form-control','readonly':'true'}), required=True)
    class Meta:
        model = Milestone   
        fields = ('name','task','overdue','subscribers','status')
        
        
    def __init__(self,user_id, *args, **kwargs):
        self.user = user_id
        super(MilestoneForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['overdue'].required = True
        self.fields['task'].required = True
