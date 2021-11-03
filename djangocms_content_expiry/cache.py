from django.core.cache import cache

from djangocms_content_expiry.conf import (
    DEFAULT_CONTENT_EXPIRY_CHANGELIST_PAGECONTENT_EXCLUSION_CACHE_EXPIRY,
)
from djangocms_content_expiry.constants import (
    CONTENT_EXPIRY_CHANGELIST_PAGECONTENT_EXCLUSION_CACHE_KEY,
)


def set_changelist_page_content_exclusion_cache(value):
    """
    Populate the cache that is set to never expire!

    :param value: A value to set the cache object with
    """
    cache.set(
        CONTENT_EXPIRY_CHANGELIST_PAGECONTENT_EXCLUSION_CACHE_KEY,
        value,
        timeout=DEFAULT_CONTENT_EXPIRY_CHANGELIST_PAGECONTENT_EXCLUSION_CACHE_EXPIRY
    )


def get_changelist_page_content_exclusion_cache():
    """
    Get the cached value if it exists.

    :returns: the cache if it is set, or None if it the key doesn't exist.
    """
    return cache.get(CONTENT_EXPIRY_CHANGELIST_PAGECONTENT_EXCLUSION_CACHE_KEY)


def unset_changelist_page_content_exclusion_cache():
    """
    Remove the cache entry including the value
    """
    cache.delete(CONTENT_EXPIRY_CHANGELIST_PAGECONTENT_EXCLUSION_CACHE_KEY)
