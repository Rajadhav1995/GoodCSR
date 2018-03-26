from projectmanagement.models import *
from projectmanagement.utils import random_string_generator
from media.models import Keywords,FileKeywords

# Here are some common methods whis we are using in 
# different places in this project
def unique_slug_generator(instance,edit, new_slug=None):
    """
    This function is for creating unique slug. Just pass object and edit=0 or 1, where 1 is for edit
    """
    slug = instance.slug
    if not edit:
        if new_slug is not None:
            slug = new_slug
        else:
            slug = slugify(instance.name)

        class_obj = instance.__class__
        qs_exists = class_obj.objects.filter(slug=slug).exists()
        if qs_exists:
            new_slug = "{slug}-{randstr}".format(
                        slug=slug,
                        randstr=random_string_generator(size=4)
                    )
            return unique_slug_generator(instance,edit,new_slug=new_slug)
    return slug

def add_keywords(keys,obj,model,edit):
    '''
    This function is to add/edit keywords for attachment file (pass 1 for 'edit' for edit keywords)
    '''
    if edit==1:
        delete = FileKeywords.objects.filter(content_type=ContentType.objects.get(model=model),object_id=obj.id)
        for i in delete:
            i.active = 0
            i.save()
    key_list = Keywords.objects.filter(active=2)
    for i in keys:
        key_obj = Keywords.objects.get_or_none(name__iexact=i.strip())
        if key_obj:
            if not key_obj.id in key_list.values_list('name',flat=True):
                key_obj = FileKeywords.objects.create(key=key_obj,content_type=ContentType.objects.get(model=model),object_id=obj.id)
        else:
            key_object = Keywords.objects.create(name=i.strip())
            key_obj = FileKeywords.objects.create(key=key_object,content_type=ContentType.objects.get(model=model),object_id=obj.id )



def add_modified_by_user(obj,request):
    '''This is function is to save the modified by user so that if any task or
    project is assigned to another user if he performs any updations to task or
    project we can display that particular user has done some changes to the 
    project or tasks '''
    temp_user = request.session.get('user_id')
    obj.modified_by = temp_user
    obj.save()
    return obj

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