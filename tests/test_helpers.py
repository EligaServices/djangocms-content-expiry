from cms.test_utils.testcases import CMSTestCase

import datetime

from djangocms_content_expiry.test_utils.factories import ContentExpiryFactory
from djangocms_content_expiry.test_utils.polls.factories import (
    PollContentWithVersionFactory,
)

from djangocms_content_expiry.helpers import get_authors


class ContentExpiryHelpersTestCase(CMSTestCase):
    def setUp(self):
        self.start_time = datetime.datetime.now()

    def test_get_authors(self):
        """
         Performance should not be affected by the get authors helper
        """
        delta_1 = datetime.timedelta(days=31)
        expire_1 = datetime.datetime.now() + delta_1
        poll_content_1 = PollContentWithVersionFactory(language="en")
        expiry_object_1 = ContentExpiryFactory(version=poll_content_1.versions.first(), expires=expire_1)

        delta_2 = datetime.timedelta(days=31)
        expire_2 = datetime.datetime.now() + delta_2
        poll_content_2 = PollContentWithVersionFactory(language="en")
        expiry_object_2 = ContentExpiryFactory(version=poll_content_2.versions.first(), expires=expire_2)

        delta_3 = datetime.timedelta(days=31)
        expire_3 = datetime.datetime.now() + delta_3
        poll_content_3 = PollContentWithVersionFactory(language="en")
        expiry_object_3 = ContentExpiryFactory(version=poll_content_3.versions.first(), expires=expire_3)

        get_authors()
        end_time = datetime.datetime.now() - self.start_time
