# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.template.defaultfilters import slugify
from constants import OPTIONAL
from django.contrib import admin
from django.views import generic
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from simple_history.models import HistoricalRecords
from thumbs import ImageWithThumbsField
from simple_history.admin import SimpleHistoryAdmin
from django.contrib.auth.models import User
from projectmanagement.models import (BaseContent,Project,UserProfile)

from django.db import models

# Create your models here.

class Menus(BaseContent):
    #-------------------#
    # Menus module
    # parent is a foriegn key
    # slug field is used
    #--------------------#
    name = models.CharField(max_length=100)
    slug = models.SlugField("SEO friendly url, use only aplhabets and hyphen", max_length=60)
    parent = models.ForeignKey('self', blank = True, null = True)
    front_link = models.CharField(max_length=512, blank=True)
    backend_link = models.CharField(max_length=512, blank=True)
    icon = models.CharField(max_length=512, blank=True)
    menu_order = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ('menu_order',)
        verbose_name_plural = 'Menus'

    def __str__(self):
    # string method to return name
        return self.name

    def get_sub_menus(self):
    # model method to filter menus based parent id
        return Menus.objects.filter(parent=self, active = 2)

    def get_sub_child(self):
        menu = Menus.objects.filter(parent=self,active=2)
        for i in menu:
            return RoleConfig.objects.filter(menu=i,view=2)

class RoleTypes(BaseContent):
    # roletype model
    name = models.CharField(unique=True,max_length=100,error_messages={'unique':"This role name already existed"})
    slug = models.SlugField("SEO friendly url, use only aplhabets and hyphen", max_length=60,null=True,blank=True)
    code = models.CharField(max_length=8,null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Role Types'

    def get_role_config(self):
        role_confs = []
        for i in Menus.objects.filter(active=2).order_by("menu_order"):
            rc,created = RoleConfig.objects.get_or_create(role=self, menu=i)
            role_confs.append(rc)
        return role_confs

    def get_menu_config(self):
        return [RoleConfig.objects.get_or_create(role=self, menu=i)
                for i in Menus.objects.filter(parent = None)]


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(RoleTypes, self).save(*args, **kwargs)

class ProjectUserRoleRelationship(BaseContent):
    project = models.ForeignKey(Project,related_name ="user_project", **OPTIONAL)
    user = models.ForeignKey(UserProfile, related_name ="project_user_role_relation",**OPTIONAL)
    role = models.ForeignKey(RoleTypes, **OPTIONAL)
    history = HistoricalRecords()

class RoleConfig(BaseContent):
    #-----------------------#
    # role config model
    # role,menu is a foriegn key
    #------------------------#
    role = models.ForeignKey(RoleTypes,blank=True,null=True)
    menu = models.ForeignKey(Menus,**OPTIONAL)
    add = models.BooleanField(default=False)
    edit = models.BooleanField(default=False)
    view = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)
    search = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType,verbose_name=_(
        'content type'),related_name="content_type_set_for_%(class)s",blank=True,null=True)
    object_id = models.IntegerField(_('object ID'),**OPTIONAL)
    relatedTo = GenericForeignKey(
        ct_field="content_type", fk_field="object_id")
    history = HistoricalRecords()

    def __str__(self):
        return self.menu.name

    class Meta:
        verbose_name_plural = 'Role Config'

    def update(self, perms):
        #----------------------#
        #providing checkbox to give permission for particular menu
        # includes add,edit,view,delete,search
        #-----------------------#
        for perm in ['add', 'edit', 'view', 'delete',
                     'search', 'mlist', 'generate',
                     'task_status',]:
            if perm in perms:
                self.__setattr__(perm, 2)
            else:
                self.__setattr__(perm, 0)
        self.save()

