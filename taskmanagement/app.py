from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

class TaskmanagementConfig(AppConfig):
    name = 'taskmanagement'
    verbose_name = _('taskmanagement')

    def ready(self):
        import taskmanagement.signals  
