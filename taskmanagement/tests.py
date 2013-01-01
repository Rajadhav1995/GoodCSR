#from django.test import TestCase

# Create your tests here.
from django.contrib.auth.models import User
from django.test import TestCase
from projectmanagement.models import *
from taskmanagement.models import *
from budgetmanagement.models import *
import datetime
from taskamanagement.views import ExpectedDatesCalculator

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


class DelayDrillTest(TestCase):
    
    def test_activity_create(self):
        project_obj = Project.objects.create(name='Sample Project1',start_date='2016-02-10',
                end_date='2018-03-20',total_budget='20000',budget_type=2,content_type=ContentType.objects.get(model='program'),object_id=0)
        budget_obj = Budget.objects.create(project=project_obj,name='Budget to Sample Project',
                start_date='2016-02-10',actual_start_date='2016-02-10',end_date='2018-04-30')
        super_obj = SuperCategory.objects.create(budget=budget_obj,name='Location',parent=None,project=project_obj)
        sub_obj = SuperCategory.objects.create(budget=budget_obj,name='Chittoor',parent=super_obj,project=project_obj)
        act_obj = Activity.objects.create(project= project_obj,super_category=sub_obj,name='Toilet Construction',
                activity_type=1,status=1,description='this is to check the activity',slug='toilet-construction')
        task_obj = Task.objects.create(activity=act_obj,start_date='2016-02-10',end_date='2018-02-14',
                    name='consrtuction of walls',slug='construct-walls',status=3,task_progress='10')
        task_obj1 = Task.objects.create(activity=act_obj,start_date='2016-02-10',end_date='2018-10-14',
                    name='consrtuction of walls',slug='construct-walls',status=3,task_progress='10')
        self.assertEqual(task_obj.end_date,datetime.datetime.now().strftime('%Y-%m-%d'))
        task_lists = Task.objects.filter(active=2).order_by('end_date')
        ExpectedDatesCalculator(task_list = task_lists)
        for i in task_lists:
            self.assertIsNotNone(i.actual_end_date)
        
        self.assertGreater(task_obj.end_date,task_obj1.end_date,'greater')
