from django.shortcuts import render
from media.models import *
from budgetmanagement.models import Tranche
from django.http import HttpResponseRedirect
from django.http import HttpResponse
import json
from django.shortcuts import get_list_or_404, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from pmu.settings import PMU_URL
from projectmanagement.models import Project,Boundary
from media.forms import AttachmentForm,ImageUpload,ImageUploadTimeline
from projectmanagement.common_method import unique_slug_generator,add_keywords
from menu_decorators import check_loggedin_access
# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
# this views is to manage media
@check_loggedin_access
def list_document(request):
    # this function will list documents of project
    #
    slug =  request.GET.get('slug')
    from django.apps import apps
    data={'Project':'projectmanagement','Task':'taskmanagement','Budget':'budgetmanagement','Userprofile':'userprofile','Media':'media'}
    app_label=data.get(request.GET.get(str('model')))
    model = apps.get_model(app_label,request.GET.get(str('model')))
    try:
        obj = model.objects.get(slug=slug)
    except:
        ids = request.GET.get('id')
        obj = model.objects.get(id=ids)
    attachment = Attachment.objects.filter(active=2,object_id=obj.id,content_type=ContentType.objects.get(model=request.GET.get('model'))).order_by('-created')
    image = PMU_URL
    key = request.GET.get('key')
    user_id = request.session.get('user_id')
    user = UserProfile.objects.get_or_none(user_reference_id = user_id)
    from taskmanagement.views import get_assigned_users
    status = get_assigned_users(user,obj)
    projectobj = obj
    project_location = ProjectLocation.objects.filter(active=2,content_type = ContentType.objects.get(model='project'),object_id=projectobj.id)
    return render(request,'attachment/listing.html',locals())
	
# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
@check_loggedin_access
def timeline_upload(request):
    # this function is to upload images in 
    # timeline (for project summary page)
    # 
    slug = request.GET.get('slug')
    user_id = request.session.get('user_id')
    user = UserProfile.objects.get(user_reference_id = user_id)
    try:
        project = Project.objects.get(slug = request.POST.get('slug'))
    except:
        project = Project.objects.get(slug=slug)
    form = ImageUploadTimeline()
    if request.method=='POST':
        form=ImageUploadTimeline(request.POST,request.FILES)
        if form.is_valid():
            f=form.save()
            f.attachment_type = 1
            f.created_by = user
            f.content_type = ContentType.objects.get(model=('project'))
            f.object_id = project.id
            f.timeline_progress = True
            # to save modified_by user to get the updates in updates sectionss
            f.modified_by = user_id
            f.save()
            return HttpResponseRedirect('/project/summary/?slug='+project.slug)
    timeline = 1
    return render(request,'taskmanagement/forms.html',locals())

# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
@check_loggedin_access
def upload_attachment(request):
    '''
    This function is to upload Image/Document 
    '''
    user_id = request.session.get('user_id')
    slug =  request.GET.get('slug')
    model =  request.GET.get('model')
    key = int(request.GET.get('key'))
    project_obj = Project.objects.get(slug=slug)
    if key==1:
        #key 1 for Document upload
        form = AttachmentForm()
    else:
        form = ImageUpload()
    if request.method == 'POST':
        if key==1:
            form = AttachmentForm(request.POST, request.FILES)
        else:
            form = ImageUpload(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.name = request.POST.get('name')
            obj.description = request.POST.get('description')
            obj.content_type=ContentType.objects.get(model=model)
            obj.object_id=project_obj.id
            obj.modified_by = user_id # to get the user who is modified in order to show updates
            obj.created_by = UserProfile.objects.get_or_none(user_reference_id=user_id)
            if key==1:
                obj.attachment_type=2
            else:
                obj.attachment_type=1
                obj.timeline_progress = False
            obj.save()
            try:
                keys = request.POST.get('keywords').split(',')
                key_model = 'Attachment'
                keywords = add_keywords(keys,obj,key_model,0)
            except Exception as e:
                e.message
            return HttpResponseRedirect('/upload/list/?slug=%s&model=%s' %(slug,model))

    return render(request,'attachment/doc_upload.html',locals())

# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
@check_loggedin_access
def edit_attachment(request):
    '''
    This function is to edit Image/Document
    '''
    ids = request.GET.get('id')
    image = PMU_URL
    obj_id =  request.GET.get('obj_id')
    if request.method == 'GET':
        slug = Project.objects.get_or_none(id=obj_id).slug
    model =  request.GET.get('model')
    obj = Attachment.objects.get(id=ids)
    keys_list = FileKeywords.objects.filter(active=2,object_id=ids).values_list('key__name',flat=True)
    keyss = ', '.join(keys_list)
    if obj.attachment_type==2:
        #key 1 for Document upload
        form = AttachmentForm(instance = obj)
        key=1
    else:
        form = ImageUpload(instance = obj)
        key=2
    if request.method == 'POST':
        instance = get_object_or_404(Attachment, id=ids)
        if key==1:
            form = AttachmentForm(request.POST, request.FILES or None, instance=instance)
        else:
            form = ImageUpload(request.POST, request.FILES or None, instance=instance)
        if form.is_valid():

            obj = form.save(commit=False)
            from projectmanagement.common_method import add_modified_by_user
            add_modified_by_user(obj,request)
            obj.save()
            # to get the user who is modified in order to show updates
            
            try:
                keys = request.POST.get('keywords').split(',')
                attach_model = 'Attachment'

                keywords = add_keywords(keys,obj,attach_model,1)
            except Exception as e:
                e.message
            return HttpResponseRedirect('/upload/list/?slug=%s&model=%s' %(request.GET.get('slug'),model))
    return render(request,'attachment/doc_upload.html',locals())

def city_list(request):
    # this function returns all city list as per 
    # state selection in project add form
    results ={}
    if request.is_ajax():
        ids =  request.GET.get('state_id')
        city_obj = Boundary.objects.filter(boundary_level=3,parent__id=ids).order_by('name').values('id','name')
        results['res']=list(city_obj)
        return HttpResponse(json.dumps(results), content_type='application/json')

#    The dict type has been reimplemented to use a more compact 
# representation based on a proposal by Raymond Hettinger and 
# similar to the PyPy dict implementation. 
# This resulted in dictionaries using 20% to 25% less memory
# when compared to Python 3.5.
#    Customization of class creation has been simplified with the new protocol.
#    The class attribute definition order is now preserved.
#    The order of elements in **kwargs now corresponds to 
# the order in which keyword arguments were passed to the function.
#    DTrace and SystemTap probing support has been added.
#    The new PYTHONMALLOC environment variable can now 
# be used to debug the interpreter memory allocation and access errors.

#Significant improvements in the standard library:

#    The asyncio module has received new features, 
# significant usability and performance improvements, and a
 # fair amount of bug fixes. Starting with Python 3.6 the 
 # asyncio module is no longer provisional and its API is considered stable.
#    A new file system path protocol has been implemented 
# to support path-like objects. All standard library functions 
# operating on paths have been updated to work with the new protocol.
#    The datetime module has gained support for Local Time Disambiguation.
#    The typing module received a number of improvements.
#    The tracemalloc module has been significantly reworked 
# and is now used to provide better output for ResourceWarning 
# as well as provide better diagnostics for memory allocation errors. 
# See the PYTHONMALLOC section for more information.

#Security improvements:

#    The new secrets module has been added to simplify 
# the generation of cryptographically strong pseudo-random 
# numbers suitable for managing secrets such as account authentication,
# tokens, and similar.
#    On Linux, os.urandom() now blocks until the system urandom 
# entropy pool is initialized to increase the security. 
# See the PEP 524 for the rationale.
#    The hashlib and ssl modules now support OpenSSL 1.1.0.
#    The default settings and feature set of the ssl module have been improved.
#    The hashlib module received support for the BLAKE2, SHA-3 
# and SHAKE hash algorithms and the scrypt() key derivation function.

# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
