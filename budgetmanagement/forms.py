from collections import OrderedDict
from django import forms
from budgetmanagement.models import Tranche,Budget
from projectmanagement.models import Project,UserProfile
from django.contrib.admin import widgets
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.contenttypes.models import ContentType
from userprofile.models import ProjectUserRoleRelationship

def get_tranche_form(slug):
	project = Project.objects.get_or_none(slug=slug)
	tt = ProjectUserRoleRelationship.objects.filter(project=project)
	class TrancheForm(forms.ModelForm):
		actual_disbursed_amount = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control'}), required=True)
		recommended_amount = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control'}), required=True)
		planned_amount = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control'}), required=True)
		name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True,max_length=200)
		recommended_by = forms.ModelChoiceField(queryset=UserProfile.objects.filter(id__in=[i.user.id for i in tt]),required=True, widget = forms.Select(attrs={'class': 'form-control'}))
		due_date = forms.DateField(widget=forms.TextInput(attrs={'class':'form-control','readonly':'true'}), required=False)
		disbursed_date = forms.DateField(widget=forms.TextInput(attrs={'class':'form-control','readonly':'true'}), required=False)
		class Meta:
			model = Tranche
			fields  = ('name','planned_amount','actual_disbursed_amount','recommended_amount',\
						'recommended_by','due_date','disbursed_date')
	return TrancheForm

class TrancheForms(forms.ModelForm):
	actual_disbursed_amount = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control'}), required=True)
	recommended_amount = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control'}), required=True)
	planned_amount = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control'}), required=True)
	name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True,max_length=200)
	# recommended_by = forms.ModelChoiceField(queryset=UserProfile.objects.filter(id__in=[i.user.id for i in tt]),required=True, widget = forms.Select(attrs={'class': 'form-control'}))
	due_date = forms.DateField(widget=forms.TextInput(attrs={'class':'form-control','readonly':'true'}), required=False)
	disbursed_date = forms.DateField(widget=forms.TextInput(attrs={'class':'form-control','readonly':'true'}), required=False)
	class Meta:
		model = Tranche
		fields  = ('name','planned_amount','actual_disbursed_amount','recommended_amount',\
					'due_date','disbursed_date')

class ProjectBudgetForm(forms.ModelForm):
	actual_start_date = forms.DateField(widget=forms.TextInput(attrs={'class':'form-control','readonly':'true'}), required=False)
	end_date = forms.DateField(widget=forms.TextInput(attrs={'class':'form-control','readonly':'true'}), required=False)
	class Meta:
		model = Budget
		fields = ('actual_start_date','end_date',)
