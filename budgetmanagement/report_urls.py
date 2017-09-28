from django.conf.urls import url
from budgetmanagement.report_generate import *


urlpatterns = [
    url(r'generation-form/$',report_form),
    url(r'detail/$',report_detail),
    url(r'quarter/update/$',genearte_report),
]
