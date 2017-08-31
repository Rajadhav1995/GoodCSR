from django.shortcuts import render
from media.models import *
from media.forms import *
from django.http import HttpResponseRedirect
from django.shortcuts import get_list_or_404, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from pmu.settings import PMU_URL
from projectmanagement.models import *

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
	
	
def timeline_upload(request):
    slug = request.GET.get('slug')
    user_id = request.session.get('user_id')
    user = UserProfile.objects.get(user_reference_id = user_id)
    try:
        project = Project.objects.get(slug = request.POST.get('slug'))
    except:
        project = Project.objects.get(slug=slug)
    form = ImageUpload()
    if request.method=='POST':
        form=ImageUpload(request.POST,request.FILES)
        if form.is_valid():
            f=form.save()
            f.attachment_type = 1
            f.created_by = user
            f.content_type = ContentType.objects.get(model=('project'))
            f.object_id = project.id
            f.save()
            return HttpResponseRedirect('/project/summary/?slug='+project.slug)
        else :
            return HttpResponseRedirect('/project/summary/?slug='+project.slug)
    else:
        form=ImageUpload()
    return render(request,'taskmanagement/forms.html',locals())
