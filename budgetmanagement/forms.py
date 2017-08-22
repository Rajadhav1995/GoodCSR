from collections import OrderedDict
from django import forms
from budgetmanagement.models import Tranche
from django.contrib.admin import widgets
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.contenttypes.models import ContentType


class TrancheForm(forms.ModelForm):
	
	class Meta:
		model = Tranche
		fields  = ('budget_period','name','planned_amount','actual_disbursed_amount','recommended_amount',\
					'recommended_by','utilized_amount','due_date','disbursed_date')