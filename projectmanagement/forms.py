from projectmanagement.models import Project,MasterCategory,UserProfile,Program,ProjectFunderRelation,ProjectParameter
from collections import OrderedDict
from django import forms
from django.contrib.auth.models import User
from django.contrib.admin import widgets
from django.core.exceptions import ValidationError
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.contenttypes.models import ContentType
from userprofile.models import (ProjectUserRoleRelationship,RoleTypes)
import bleach
from django.conf import settings

# Django provides a range of tools and libraries 
# to help you build forms to accept input from 
# site visitors, and then process and respond to the input.
BUDGET_TYPE = ((1,'Yearly'),(2,'Quarterly'),(3,'Half Yearly'))
STATUS_CHOICES = ((0,''),(1, 'Open'), (2, 'Close'), (3, 'Ongoing'),)
# this is form for adding and editing project
class ProjectForm(forms.ModelForm):
	name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True,max_length=200)
	target_beneficiaries = forms.ModelMultipleChoiceField(queryset = MasterCategory.objects.filter(parent__slug='target-beneficiarys'),
                        required = False,
                        widget = forms.SelectMultiple(attrs = {'class': 'form-control'}))
	cause_area = forms.ModelMultipleChoiceField(queryset = MasterCategory.objects.filter(parent__slug='cause-area'),
                        required = False,
                        widget = forms.SelectMultiple(attrs = {'class': 'form-control'}))
	total_budget = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control'}), required=True)
	no_of_beneficiaries = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control'}), required=True)
	budget_type = forms.ChoiceField(choices = BUDGET_TYPE,widget = forms.Select(attrs={'class': 'form-control'}))
	project_status = forms.ChoiceField(choices = STATUS_CHOICES,initial='1',required=True,widget = forms.Select(attrs={'class': 'form-control'}))
	start_date = forms.DateField(widget=forms.TextInput(attrs={'class':'form-control','readonly':'true'}), required=False)
	end_date = forms.DateField(widget=forms.TextInput(attrs={'class':'form-control','readonly':'true'}), required=False)
	duration = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control','readonly':'true'}), required=True)
	class Meta:
		model = Project
		fields  = ('name','start_date','end_date','total_budget','budget_type',\
        			'project_status','duration','summary','program_aim','no_of_beneficiaries','cause_area','target_beneficiaries')
    

	def clean(self):
		# this is to validate project name
		cleaned_data = self.cleaned_data
		if Project.objects.filter(name=cleaned_data['name']).exclude(pk=self.instance.id).count() > 0:
			try:
				Project.objects.get(name=cleaned_data['name'])
			except Project.DoesNotExist:
				pass
			else:
				raise ValidationError('Project with this Name already exists for this problem')

			# Always return cleaned_data
		return cleaned_data
		
	def clean_name(self):
		name = self.cleaned_data.get('name', '')
		cleaned_text = bleach.clean(name, settings.BLEACH_VALID_TAGS, settings.BLEACH_VALID_ATTRS, settings.BLEACH_VALID_STYLES)
		return cleaned_text
    
	def clean_summary(self):
		summary = self.cleaned_data.get('summary', '')
		cleaned_text = bleach.clean(summary, settings.BLEACH_VALID_TAGS, settings.BLEACH_VALID_ATTRS, settings.BLEACH_VALID_STYLES)
		return cleaned_text
	def clean_program_aim(self):
		program_aim = self.cleaned_data.get('program_aim', '')
		cleaned_text = bleach.clean(program_aim, settings.BLEACH_VALID_TAGS, settings.BLEACH_VALID_ATTRS, settings.BLEACH_VALID_STYLES)
		return cleaned_text

# Django provides a range of tools and libraries 
# to help you build forms to accept input from 
# site visitors, and then process and respond to the input.
class ProjectMappingForm(forms.ModelForm):
	# this form is to map funder and implementation 
	# parnert with the project
	# 
	class Meta:
		model = ProjectFunderRelation
		fields  = ('project','funder','implementation_partner','total_budget')

class ProjectUserRoleRelationshipForm(forms.ModelForm):
	# this form is to map funder and implementation 
	# parnert with the project
	# 
    user = forms.ModelChoiceField(queryset=UserProfile.objects.filter(),required=True, widget = forms.Select(attrs={'class': 'form-control'}))
    role = forms.ModelChoiceField(queryset=RoleTypes.objects.filter(active=2),required=True, widget = forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = ProjectUserRoleRelationship
        fields = ('user','role')

# Django provides a range of tools and libraries 
# to help you build forms to accept input from 
# site visitors, and then process and respond to the input.
PARAMETER_TYPE_CHOICES=(('PIN','Pie chart Numbers'),
                          ('PIP', 'Pie Chart Percent'),
                          ('NUM','Number'),
                          ('PER','Percent'),
                          ('CUR','Currency'))
class ProjectParameterForm(forms.ModelForm):
	# this form is to add project parameter
	# 
	name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=False,max_length=200)
	budget_type = forms.ChoiceField(choices = PARAMETER_TYPE_CHOICES,widget = forms.Select(attrs={'class': 'form-control'}))
	class Meta:
		model = ProjectParameter
		fields  = ('parameter_type','name')
