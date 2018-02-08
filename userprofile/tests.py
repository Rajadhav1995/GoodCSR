# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from userprofile.models import *

# Create your tests here.

class UserRoleListTestCase(TestCase):

    def menucount(self):
        menulist = Menus.objects.filter(active=2)
        count = menulist.count()
        self.assertEqual(count, 22)
    
    def menucountwrong(self):
        menulist = Menus.objects.filter(active=2)
        count = menulist.count()
        self.assertEqual(count, 24)
