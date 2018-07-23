from projectmanagement.models import Project,MasterCategory,UserProfile,Program,ProjectFunderRelation
from collections import OrderedDict
from django import forms
from media.models import Attachment,Note
from django.contrib.admin import widgets
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from media.models import ContactPersonInformation
from captcha.fields import ReCaptchaField
from django.utils.translation import gettext as _
from django.conf import settings
import requests
from django.forms import ClearableFileInput
from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget

import os

# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
class MyClearableFileInput(ClearableFileInput):
     template_with_initial = '<br>%(input_text)s: %(input)s'
# Django provides a range of tools and libraries 
# to help you build forms to accept input from 
# site visitors, and then process and respond to the input.
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
    def clean_attachment_file(self):
        content = self.cleaned_data.get('attachment_file')
        content_type = content.content_type.split('/')[1] if content else ''
        if content and content_type in settings.DOC_CONTENT_TYPE and os.path.splitext(content.name)[1] in settings.DOC_EXTENSION_LIST:
            if content.size > settings.MAX_UPLOAD_SIZE:
                self._errors['attachment_file']=self.error_class(['File size 5 Mb or less'])
        else:
            self._errors['attachment_file']=self.error_class(['File format not supported'])
        return content
# Django provides a range of tools and libraries 
# to help you build forms to accept input from 
# site visitors, and then process and respond to the input.
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

    def clean_attachment_file(self):
        content = self.cleaned_data.get('attachment_file')
        content_type = content.content_type.split('/')[0] if content else ''
        if content_type == 'image' and content:
            if content.size > settings.IMG_UPLOAD_SIZE:
                self._errors['attachment_file']=self.error_class(['Image size 1 Mb or less'])
        else:
            self._errors['attachment_file']=self.error_class(['This image format is not supported'])
        return content

# Django provides a range of tools and libraries 
# to help you build forms to accept input from 1
# site visitors, and then process and respond to the input.
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
    def clean_attachment_file(self):
        content = self.cleaned_data.get('attachment_file')
        content_type = content.content_type.split('/')[0] if content else ''
        if content_type == 'image' and content:
            if content.size > settings.IMG_UPLOAD_SIZE:
                self._errors['attachment_file']=self.error_class(['Image size 1 Mb or less'])
        else:
            self._errors['attachment_file']=self.error_class(['This image format is not supported'])
        return content
# Django provides a range of tools and libraries 
# to help you build forms to accept input from 
# site visitors, and then process and respond to the input.
# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.


class ContactPersonForm(forms.ModelForm):
    '''
    This is model form is to save contact information of visitor 
    '''
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True,max_length=200)
    email = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True,max_length=200)
    organization_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), required=True,max_length=200)
    mobile_number = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control'}), required=True)
    message = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control text_area'}), required=True)
#    captcha = ReCaptchaField(attrs={'theme' : 'white'}, required=True)
    captcha = ReCaptchaField(widget=ReCaptchaWidget())

    class Meta:
        model = ContactPersonInformation
        fields  = ('name','email','organization_name','mobile_number','message')

# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
class NoteForm(forms.ModelForm):
    '''
    This is model form to create nte in project update wall
    '''
    comment = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control text_area'}), required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control text_area'}), required=True)
    attachment_file = forms.ImageField(label=_('Attach File'),required=False, error_messages = {'invalid':_("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = Note
        fields  = ('description','attachment_file','comment')
        widgets = {
            "file": MyClearableFileInput(),
        }
