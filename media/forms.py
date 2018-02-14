from projectmanagement.models import Project,MasterCategory,UserProfile,Program,ProjectFunderRelation
from collections import OrderedDict
from django import forms
from media.models import Attachment
from django.contrib.admin import widgets
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from media.models import ContactPersonInformation
# from captcha.fields import ReCaptchaField
from django.utils.translation import gettext as _
from django.conf import settings
import requests
from django.forms import ClearableFileInput

class MyClearableFileInput(ClearableFileInput):
     template_with_initial = '<br>%(input_text)s: %(input)s'

DOCUMENT_TYPE = ((1,'Excel'),(2,'PDF'),(3,'PPT'),(4,'Word Document'))
class AttachmentForm(forms.ModelForm):
    '''
    This is model form to upload attachment (type: doc, pdf,ppt) for project
    '''
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True,max_length=200)
    document_type = forms.ChoiceField(choices = DOCUMENT_TYPE,widget = forms.Select(attrs={'class': 'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control text_area'}), required=True)
    attachment_file = forms.FileField(label=_('Company Logo'),required=False, error_messages = {'invalid':_("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = Attachment
        fields  = ('attachment_file','name','document_type','description')
        widgets = {
            "file": MyClearableFileInput(),
        }


class ImageUpload(forms.ModelForm):
    '''
    This is model form to upload Image for Project
    '''
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True,max_length=200)
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control text_area'}), required=True)
    attachment_file = forms.ImageField(label=_('Company Logo'),required=False, error_messages = {'invalid':_("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = Attachment
        fields  = ('description','attachment_file','name')
        widgets = {
            "file": MyClearableFileInput(),
        }

class ImageUploadTimeline(forms.ModelForm):
    '''
    This is model form to upload Image for Project
    '''
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True,max_length=200)
    date = forms.DateTimeField(widget=forms.TextInput(attrs={'class':'form-control','readonly':'true','placeholder':'Please Select Date'}), required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control text_area'}), required=True)
    class Meta:
        model = Attachment
        fields  = ('date','description','attachment_file','name')

class ContactPersonForm(forms.ModelForm):
    '''
    This is model form is to save contact information of visitor 
    '''
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True,max_length=200)
    email = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True,max_length=200)
    organization_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True,max_length=200)
    mobile_number = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control'}), required=True)
    message = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control text_area'}), required=True)
    # captcha = ReCaptchaField(attrs={'theme' : 'white'}, required=True)

    class Meta:
        model = ContactPersonInformation
        fields  = ('name','email','organization_name','mobile_number','message')