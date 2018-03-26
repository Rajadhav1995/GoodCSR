from django.conf.urls import url
from budgetmanagement.report_generate import *
from budgetmanagement.remove_pdf_view import remove_functionality_pdf_view
from budgetmanagement.report_download_pdf import (
									pdfconverter,pdf_header,pdf_footer)


# this are URLs are related with the Report generation
urlpatterns = [
    url(r'generation-form/$',report_form),
    url(r'remove/detail/$',remove_functionality_pdf_view),
    url(r'detail/$',report_detail),
    url(r'^section-form/$',report_section_form),
    url(r'listing/$',report_listing),
    url(r'display/blocks/$',display_blocks),
#    url(r'^download/pdf/$',download_report_generation),
    url(r'final/design/$',finalreportdesign),
#    url(r'pdf/view/$',html_to_pdf_view),
    url(r'pdf/view/$',pdfconverter),
    url(r'pdf/view/new/$',pdfconverter),
    url(r'pdf/view/header/$',pdf_header),
    url(r'pdf/view/footer/$',pdf_footer),
    url(r'removed/fields/$',save_removed_fields),
    url(r'adding/fields/$',save_added_fields),
]
