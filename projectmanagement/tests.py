from django.test import TestCase
from projectmanagement.models import ProjectParameter,ProjectParameterValue,Project


class ParameterTestCase(TestCase):
	def setUp(self):
		project = Project.objects.latest_one()
		parameter = ProjectParameter.objects.create(project=project, name='Test Parameter')
		ProjectParameterValue.objects.create(keyparameter=parameter,parameter_value=45)

	def test_parameter(self):
		parameter = ProjectParameter.objects.latest_one()
		para_value = ProjectParameterValue.objects.get(keyparameter=parameter)
		para_value.parameter_value = 100
		para_value.save()
		self.assertEqual(para_value.parameter_value,100)