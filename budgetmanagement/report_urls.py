from django.conf.urls import url
from budgetmanagement.report_generate import *


urlpatterns = [
    url(r'generation-form/$',report_form),
    url(r'detail/$',report_detail),
    url(r'^section-form/$',report_section_form),
    url(r'quarter/update/$',generate_report),
    url(r'listing/$',report_listing),
    url(r'display/blocks/$',display_blocks),
    url(r'^download/pdf/$',download_report_generation),
    url(r'survey/quarter/$',quartergeneratereport),
    url(r'final/design/$',finalreportdesign),

]
