from django.conf import settings


# Default range filter control in days
DEFAULT_RANGEFILTER_DELTA = getattr(
    settings, "CMS_CONTENT_EXPIRY_DEFAULT_RANGEFILTER_DELTA", 30
)

# Default Content Expiry duration in months
DEFAULT_CONTENT_EXPIRY_DURATION = getattr(
    settings, "CMS_CONTENT_EXPIRY_DEFAULT_CONTENT_EXPIRY_DURATION", 12
)

# Default Content Expiry duration in months
DEFAULT_CONTENT_EXPIRY_EXPORT_DATE_FORMAT = getattr(
    settings, "CMS_CONTENT_EXPIRY_DEFAULT_CONTENT_EXPIRY_EXPORT_DATE_FORMAT", "%Y/%m/%d %H:%M %z"
)

# Default Content Expiry changelist page content exclusion cache expiration duration in seconds
DEFAULT_CONTENT_EXPIRY_CHANGELIST_PAGECONTENT_EXCLUSION_CACHE_EXPIRY = getattr(
    settings, "CMS_DEFAULT_CONTENT_EXPIRY_CHANGELIST_PAGECONTENT_EXCLUSION_CACHE_EXPIRY", 300
)
