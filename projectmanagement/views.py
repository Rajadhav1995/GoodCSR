from django.shortcuts import render
from projectmanagement.models import *
from projectmanagement.forms import *
from django.http import HttpResponseRedirect
# Create your views here.

def create_project(request):
	ids =  request.GET.get('id')
	obj = Project.objects.get(id=ids)
	try:
		ids =  request.GET.get('id')
		obj = Project.objects.get(id=ids)
		form = ProjectForm(instance = obj)
	except:
		form = ProjectForm()
	if request.method == 'POST':

		try:
			instance = get_object_or_404(Project, id=ids)
			form = ProjectForm(request.POST,request.FILES or None, instance=instance)
		except:
			form = ProjectForm(request.POST,request.FILES)
		if form.is_valid():
			obj = form.save(commit=False)
			obj.content_type = ContentType.objects.get(model="Program")
			obj.object_id = 23
			obj.save()
			return HttpResponseRedirect('/project/add/')
	return render(request,'project_edit.html',locals())

def project_list(request):
	obj_list = Project.objects.all()
	return render(request,'listing.html',locals())	