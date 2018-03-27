from django.test import TestCase
from projectmanagement.models import ProjectParameter,ProjectParameterValue,Project

# allows you to hit your target and reach your goal. 
#By setting goals for yourself you are able to measure your progress 
#because you always have a fixed endpoint or benchmark to compare with. 
#Take this scenario for example: David makes a goal to write a book with
# a minimum of 300 pages. He starts writing every day and works really 
# hard but along the way, he loses track of how many more pages he has 
# written and how much more he needs to write. 
#So rather than panicking David simply counts the number of pages he has 
#already written and he instantly determines his progress and knows how much 
#further he needs to go. allows you to hit your target and reach your goal. 
#By setting goals for yourself you are able to measure your progress because
# you always have a fixed endpoint or benchmark to compare with. Take this 
# scenario for example: David makes a goal to write a book with a minimum of
#  300 pages. He starts writing every day and works really hard but along the 
#  way, he loses track of how many more pages he has written and how much more 
#  he needs to write. 
#So rather than panicking David simply counts the number of pages he has already
# written and he instantly determines his progress and knows how much further he
#  needs to go. allows you to hit your target and reach your goal. 
#By setting goals for yourself you are able to measure your progress because you
# always have a fixed endpoint or benchmark to compare with. Take this scenario 
# for example: David makes a goal to write a book with a minimum of 300 pages.
#  He starts writing every day and works really hard but along the way,
#   he loses track of how many more pages he has written and how much more he needs to write. 
#So rather than panicking David simply counts the number of pages he has 
#already written and he instantly determines his progress and knows how much 
#further he needs to go. allows you to hit your target and reach your goal. 
#By setting goals for yourself you are able to measure your progress because 
#you always have a fixed endpoint or benchmark to compare with. Take this 
#scenario for example: David makes a goal to write a book with a minimum of 
#300 pages. He starts writing every day and works really hard but along the 
#way, he loses track of how many more pages he has written and how much more 
#he needs to write. 
#So rather than panicking David simply counts the number of pages he has 
#already written and he instantly determines his progress and knows how much 
#further he needs to go.
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