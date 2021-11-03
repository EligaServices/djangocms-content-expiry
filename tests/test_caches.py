from cms.api import create_page
from cms.test_utils.testcases import CMSTestCase

from djangocms_content_expiry.cache import (
    get_changelist_page_content_exclusion_cache,
    set_changelist_page_content_exclusion_cache,
)
from djangocms_content_expiry.test_utils.polls.factories import PollVersionFactory


class ContentExpiryPageContentCacheSignalHandlerTestCase(CMSTestCase):
    def test_content_expiry_cache_clear_signal_pagecontent(self):
        """
        Creating a new PageContent object should empty the existing cache entry
        """
        value = [1]

        set_changelist_page_content_exclusion_cache(value)
        cached_value = get_changelist_page_content_exclusion_cache()

        self.assertEqual(cached_value, value)

        # Creating a page which should fire the pagecontent changed signal
        create_page(
            title="home",
            template="page.html",
            language="en",
            created_by=self.get_superuser()
        )

        cached_value = get_changelist_page_content_exclusion_cache()

        # The cache should now be empty
        self.assertNotEqual(cached_value, value)
        self.assertEqual(cached_value, None)

    def test_content_expiry_cache_clear_signal_other(self):
        """
        Creating a new  object should empty the existing cache entry
        """
        value = [1]

        set_changelist_page_content_exclusion_cache(value)
        cached_value = get_changelist_page_content_exclusion_cache()

        self.assertEqual(cached_value, value)

        # Create a page which should fire the pagecontent changed signal
        PollVersionFactory()

        cached_value = get_changelist_page_content_exclusion_cache()

        # The cache should now be empty
        self.assertEqual(cached_value, value)
        self.assertNotEqual(cached_value, None)
