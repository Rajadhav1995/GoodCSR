from django.shortcuts import render
from media.models import *
from media.forms import *
from django.http import HttpResponseRedirect
from django.shortcuts import get_list_or_404, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from pmu.settings import PMU_URL

# def add_doccument(request):
# 	ids =  request.GET.get('id')
# 	model = eval(request.GET.get('model'))
# 	form = AttachmentForm()
# 	if request.method == 'POST':
		
# 		attach = Attachment.objects.create(attachment_file=attach_file,name=desc,\
#                     content_type=ContentType.objects.get(model=model),object_id=obj_id)

def list_document(request):
	slug =  request.GET.get('slug')
	model = eval(request.GET.get('model'))
	obj = model.objects.get(slug=slug)
	attachment = Attachment.objects.filter(object_id=obj.id,content_type=ContentType.objects.get(model=request.GET.get('model')))
	image = PMU_URL
	return render(request,'attachment/listing.html',locals())
