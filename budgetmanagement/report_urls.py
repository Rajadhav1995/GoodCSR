from django.conf.urls import url
from budgetmanagement.report_generate import *
from budgetmanagement.report_download_pdf import download_report_generation,save_screenshots


urlpatterns = [
    url(r'generation-form/$',report_form),
    url(r'detail/$',report_detail),
    url(r'^section-form/$',report_section_form),
#    url(r'quarter/update/$',generate_report),
    url(r'listing/$',report_listing),
    url(r'display/blocks/$',display_blocks),
    url(r'^download/pdf/$',download_report_generation),
    url(r'final/design/$',finalreportdesign),
    # url(r'pdf/view/$',html_to_pdf_view),
    url(r'save/image/$',save_screenshots),
    url(r'pdf/view/$',html_to_pdf_view),
    url(r'save/exit/$',report_save_exit)
]
