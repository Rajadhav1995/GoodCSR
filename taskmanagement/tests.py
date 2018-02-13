#from django.test import TestCase

# Create your tests here.
from django.contrib.auth.models import User
from django.test import TestCase
from projectmanagement.models import *
from taskmanagement.models import *



 class LogInTest(TestCase):
     def setUp(self):
         self.credentials = {
             'username': 'mahiti',
             'password': 'goodcsr@#1234'}
         User.objects.create(**self.credentials)
     def test_login(self):
         # send login data
         response = self.client.post('/login/', self.credentials, follow=True)
         # should be logged in now
         self.assertFalse(response.context['user'].is_active)
        
    def test_admin(self):
        user = User.objects.get(username='mahiti')
        self.assertNotEqual(user.username,'mahiti')

        
    def test_user_profile(self):
        user = UserProfile.objects.get(name='mahiti')
        self.assertEqual(user.is_admin_user,False)
        
    def test_get_tasks(self):
        task_list = Task.objects.filter(active=2)
        self.assertEqual(len(task_list),4)



