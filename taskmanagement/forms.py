import re
from collections import OrderedDict
from django import forms
from django.contrib.auth.models import User
from django.contrib.admin import widgets
from ckeditor.widgets import CKEditorWidget
from ckeditor_uploader.fields import RichTextUploadingField
from django.core.validators import *
from django.core.exceptions import ValidationError
from taskmanagement.models import *

class ActivityForm(forms.ModelForm):
    
    class Meta:
        model = Activity
        fields  = ('name','super_category','activity_type','description','status')
        

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('name','activity','start_date','end_date','actual_start_date','actual_end_date','status')
