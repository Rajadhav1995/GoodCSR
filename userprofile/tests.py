# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from userprofile.models import *
from projectmanagement.models import *

# Create your tests here.

class UserRoleListTestCase(TestCase):

    def test_menu_create(self):
        menu = Menus.objects.create(name="My Tasks",slug="my-tasks")

    def test_menucount(self):
        menu = Menus.objects.create(name="My Tasks",slug="my-tasks")
        menulist = Menus.objects.filter()
        count = menulist.count()
        self.assertEqual(count, 1,"perfect%s"%count)
    
    def test_menucountwrong(self):
        menu = self.test_menu_create()
        menulist = Menus.objects.filter()
        count = menulist.count()
        self.assertEqual(count, 22)

    def test_user_create(self):
        userprofileobj = UserProfile.objects.create(email = "meghana.com@mahiti.org")

    def test_role_create(self):
        roleobj = RoleTypes.objects.create(name = "Funder",slug="funder")

    def test_user_role_tag(self):
        user = self.test_user_create()
        user = UserProfile.objects.filter()[0]
        roleobj = self.test_role_create()
        roleobj = RoleTypes.objects.filter()[0]
        roletypeuser = UserRoles.objects.create(user = user)
        roletypeuser.role_type.add( roleobj)
        roletypeuser.save()

    def test_role_config(self):
        roleobj = self.test_role_create()
        menu = self.test_menu_create()
        menu = Menus.objects.filter()[0]
        roleconfig = RoleConfig.objects.create(role = roleobj,menu = menu)
        roleconfig.add = True
        roleconfig.save()

    def test_user_permission(self):
        userprofileobj = UserProfile.objects.create(email = "meghana.com@mahiti.org")
        menu = Menus.objects.create(name="My Tasks",slug="my-tasks")
        roleobj = RoleTypes.objects.create(name = "PMO",slug="pmo")
        roletypeuser = UserRoles.objects.create(user = userprofileobj)
        roletypeuser.role_type.add( roleobj)
        user_id = UserProfile.objects.filter()[0]
        user_roleobj = UserRoles.objects.filter(user = user_id).values_list('role_type',flat=True)
        if user_roleobj :
            user_roleobj = user_roleobj[0]
            menu = Menus.objects.get(slug = "my-tasks")
            roleconfig = self.test_role_config()
            roleconfig = RoleConfig.objects.filter()[0]
            self.assertEqual(True,roleconfig.add,"matches")
        else:
            self.assertEqual(False,False,"nothing is matching.")
