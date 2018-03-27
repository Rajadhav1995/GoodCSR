# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

# When working with any programming language, you include comments
# in the code to notate your work. This details what certain parts 
# know what you were up to when you wrote the code. This is a necessary
# practice, and good developers make heavy use of the comment system. 
# Without it, things can get real confusing, real fast.
# 
class TaskmanagementConfig(AppConfig):
    name = 'taskmanagement'
    verbose_name = _('taskmanagement')

    def ready(self):
        import taskmanagement.signals  
