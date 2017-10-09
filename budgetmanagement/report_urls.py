from django.conf.urls import url
from budgetmanagement.report_generate import *


urlpatterns = [
    url(r'generation-form/$',report_form),
    url(r'detail/$',report_detail),
    url(r'quarter/update/$',genearte_report),
    url(r'generate/$',report_create),
    url(r'listing/$',report_listing),

]
