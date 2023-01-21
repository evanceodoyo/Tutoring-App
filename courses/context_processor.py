import datetime

from django.conf import settings

date_established = datetime.datetime(2022, 4, 1, 12, 0)
today = datetime.datetime.now()
days_since_established = round((today - date_established).days / 365)


def global_context_renderer(request):
    return {
        "site_name": settings.SITE_NAME,
        "page_title": settings.PAGE_TITLE,
        "meta_keywords": settings.META_KEYWORDS,
        "meta_description": settings.META_DESCRIPTION,
        "location": "Nairobi",
        "address": "Kenyatta Avenue",
        "telephone": "+254712345678",
        "alternate_telephone": "",
        "info_mail": "info@codeafrik.com",
        "support_email": "support@codeafrik.com",
        "years_since_established": days_since_established,
    }
