from django.shortcuts import render
from media.models import *
from media.forms import *
from django.http import HttpResponseRedirect
from django.shortcuts import get_list_or_404, get_object_or_404
from django.contrib.contenttypes.models import ContentType

def add_doccument(request):
	ids =  request.GET.get('id')
	model = eval(request.GET.get('model'))
	form = AttachmentForm()
	if request.method == 'POST':
		
		attach = Attachment.objects.create(attachment_file=attach_file,name=desc,\
                    content_type=ContentType.objects.get(model=model),object_id=obj_id)