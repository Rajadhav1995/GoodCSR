from projectmanagement.models import Project,MasterCategory,UserProfile,Program
from collections import OrderedDict
from django import forms
from django.contrib.auth.models import User
from django.contrib.admin import widgets
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.contenttypes.models import ContentType

BUDGET_TYPE = ((1,'Yearly'),(2,'Quarterly'),(3,'Half Yearly'))
STATUS_CHOICES = ((0,''),(1, 'Open'), (2, 'Close'), (3, 'Ongoing'),)
class ProjectForm(forms.ModelForm):
	name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=False,max_length=200)
	target_beneficiaries = forms.ModelMultipleChoiceField(queryset = MasterCategory.objects.filter(parent__slug='target-beneficiarys'),
                        required = False,
                        widget = forms.SelectMultiple(attrs = {'class': 'form-control'}))
	cause_area = forms.ModelMultipleChoiceField(queryset = MasterCategory.objects.filter(parent__slug='cause-area'),
                        required = False,
                        widget = forms.SelectMultiple(attrs = {'class': 'form-control'}))
	total_budget = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control'}), required=True)
	no_of_beneficiaries = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control'}), required=True)
	budget_type = forms.ChoiceField(choices = BUDGET_TYPE,widget = forms.Select(attrs={'class': 'form-control'}))
	created_by = forms.ModelChoiceField(queryset=UserProfile.objects.filter(),required=True, widget = forms.Select(attrs={'class': 'form-control'}))
	program = forms.ModelChoiceField(queryset=Program.objects.filter(),required=True, widget = forms.Select(attrs={'class': 'form-control'}))
	project_status = forms.ChoiceField(choices = STATUS_CHOICES,required=True,widget = forms.Select(attrs={'class': 'form-control'}))
	start_date = forms.DateField(widget=forms.TextInput(attrs={'class':'form-control','readonly':'true'}), required=False)
	end_date = forms.DateField(widget=forms.TextInput(attrs={'class':'form-control','readonly':'true'}), required=False)
	duration = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control','readonly':'true'}), required=True)
	class Meta:
		model = Project
		fields  = ('program','name','start_date','end_date','total_budget','budget_type','created_by',\
        			'project_status','duration','summary','no_of_beneficiaries','cause_area','target_beneficiaries',\
        			'location')