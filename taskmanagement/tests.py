#from django.test import TestCase

# Create your tests here.
from django.contrib.auth.models import User
from django.test import TestCase

class LogInTest(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'mahiti1',
            'password': 'goodcsr@#1234'}
        User.objects.create(**self.credentials)
    def test_login(self):
        # send login data
        response = self.client.post('/login/', self.credentials, follow=True)
        # should be logged in now
        self.assertFalse(response.context['user'].is_active)



