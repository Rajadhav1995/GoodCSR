from projectmanagement.models import Project,MasterCategory,UserProfile,Program,ProjectFunderRelation,ProjectParameter
from collections import OrderedDict
from django import forms
from django.contrib.auth.models import User
from django.contrib.admin import widgets
from django.core.exceptions import ValidationError
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.contenttypes.models import ContentType
from userprofile.models import (ProjectUserRoleRelationship,RoleTypes)

BUDGET_TYPE = ((1,'Yearly'),(2,'Quarterly'),(3,'Half Yearly'))
STATUS_CHOICES = ((0,''),(1, 'Open'), (2, 'Close'), (3, 'Ongoing'),)
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


class ProjectMappingForm(forms.ModelForm):
	class Meta:
		model = ProjectFunderRelation
		fields  = ('project','funder','implementation_partner','total_budget')

class ProjectUserRoleRelationshipForm(forms.ModelForm):

    user = forms.ModelChoiceField(queryset=UserProfile.objects.filter(),required=True, widget = forms.Select(attrs={'class': 'form-control'}))
    role = forms.ModelChoiceField(queryset=RoleTypes.objects.filter(active=2),required=True, widget = forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = ProjectUserRoleRelationship
        fields = ('user','role')


PARAMETER_TYPE_CHOICES=(('PIN','Pie chart Numbers'),
                          ('PIP', 'Pie Chart Percent'),
                          ('NUM','Number'),
                          ('PER','Percent'),
                          ('CUR','Currency'))
class ProjectParameterForm(forms.ModelForm):
	name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=False,max_length=200)
	budget_type = forms.ChoiceField(choices = PARAMETER_TYPE_CHOICES,widget = forms.Select(attrs={'class': 'form-control'}))
	class Meta:
		model = ProjectParameter
		fields  = ('parameter_type','name')
