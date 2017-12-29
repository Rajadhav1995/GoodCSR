from projectmanagement.models import *
from projectmanagement.utils import random_string_generator
from media.models import Keywords,FileKeywords

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
