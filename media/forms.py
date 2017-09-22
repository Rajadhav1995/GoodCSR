from projectmanagement.models import Project,MasterCategory,UserProfile,Program,ProjectFunderRelation
from collections import OrderedDict
from django import forms
from media.models import Attachment
from django.contrib.admin import widgets
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.contenttypes.models import ContentType
from media.models import ContactPersonInformation
DOCUMENT_TYPE = ((1,'Excel'),(2,'PDF'),(3,'PPT'),(4,'Word Document'))
class AttachmentForm(forms.ModelForm):
    '''
    This is model form to upload attachment (type: doc, pdf,ppt) for project
    '''
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True,max_length=200)
    date = forms.DateField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Please Select Date','readonly':'true'}))
    document_type = forms.ChoiceField(choices = DOCUMENT_TYPE,widget = forms.Select(attrs={'class': 'form-control'}))
    description = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control text_area'}), required=True)
    class Meta:
        model = Attachment
        fields  = ('attachment_file','name','date','document_type')

class ImageUpload(forms.ModelForm):
    '''
    This is model form to upload Image for Project
    '''
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True,max_length=200)
    date = forms.DateTimeField(widget=forms.TextInput(attrs={'class':'form-control','readonly':'true','placeholder':'Please Select Date'}), required=True)
    description = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control text_area'}), required=True)
    class Meta:
        model = Attachment
        fields  = ('date','description','attachment_file')

class ContactPersonForm(forms.ModelForm):
    '''
    This is model form is to save contact information of visitor 
    '''
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True,max_length=200)
    email = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True,max_length=200)
    organization_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True,max_length=200)
    mobile_number = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True,max_length=200)
    message = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control text_area'}), required=True)

    class Meta:
        model = ContactPersonInformation
        fields  = ('name','email','organization_name','mobile_number','message')