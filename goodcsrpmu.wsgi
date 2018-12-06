import os
import sys
import site

prev_sys_path = list(sys.path)
site.addsitedir('/usr/local/lib/python2.7/site-packages')

sys.path.append('/home/goodcsr');
sys.path.append('/home/goodcsr/GoodCSR-PMU');

os.environ['DJANGO_SETTINGS_MODULE'] = 'pmu.settings'

sys.path.extend([
   '/home/goodcsr/pmu1.11/lib/python2.7/site-packages',
   '/home/goodcsr/pmu1.11/python2.7/site-packages/django/contrib/admindocs',
])
new_sys_path = [p for p in sys.path if p not in prev_sys_path]
for item in new_sys_path:
    sys.path.remove(item)
sys.path[:0] = new_sys_path

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
