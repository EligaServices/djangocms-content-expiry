import datetime

from cms.test_utils.testcases import CMSTestCase

from djangocms_content_expiry.models import ContentExpiry
from djangocms_content_expiry.test_utils.factories import ContentExpiryFactory
from djangocms_content_expiry.test_utils.polls.factories import PollContentWithVersionFactory


class ContentExpiryChangelistFilterTestCase(CMSTestCase):

    def test_expired_filter_default_setting(self):
        self.assertSetEqual("TODO: The is_default settings should be tested and enforced", "")

    def test_expired_filter_view_expired_at_boundaries(self):
        """
        Check the boundaries of the Expired by filter. The dates are
        set to check that only records due to expire are shown with a filter value set at 30 days
        """
        # Record that is expired by 1 day
        delta_1 = datetime.timedelta(days=1)
        expire_at_1 = datetime.datetime.now() - delta_1
        poll_content_1 = PollContentWithVersionFactory(language="en")
        content_expiry_1 = ContentExpiryFactory(version=poll_content_1.versions.first(), expires=expire_at_1)

        # Record that is set to expire today
        expire_at_2 = datetime.datetime.now()
        poll_content_2 = PollContentWithVersionFactory(language="en")
        content_expiry_2 = ContentExpiryFactory(version=poll_content_2.versions.first(), expires=expire_at_2)

        # Record that is set to expire tomorrow
        delta_3 = datetime.timedelta(days=1)
        expire_at_3 = datetime.datetime.now() + delta_3
        poll_content_3 = PollContentWithVersionFactory(language="en")
        content_expiry_3 = ContentExpiryFactory(version=poll_content_3.versions.first(), expires=expire_at_3)

        # Record that is set to expire in 29 days
        delta_4 = datetime.timedelta(days=29)
        expire_at_4 = datetime.datetime.now() + delta_4
        poll_content_4 = PollContentWithVersionFactory(language="en")
        content_expiry_4 = ContentExpiryFactory(version=poll_content_4.versions.first(), expires=expire_at_4)

        # Record that is set to expire in 30 days
        delta_5 = datetime.timedelta(days=30)
        expire_at_5 = datetime.datetime.now() + delta_5
        poll_content_5 = PollContentWithVersionFactory(language="en")
        content_expiry_5 = ContentExpiryFactory(version=poll_content_5.versions.first(), expires=expire_at_5)

        # Record that is set to expire in 31 days
        delta_6 = datetime.timedelta(days=31)
        expire_at_6 = datetime.datetime.now() + delta_6
        poll_content_6 = PollContentWithVersionFactory(language="en")
        ContentExpiryFactory(version=poll_content_6.versions.first(), expires=expire_at_6)

        with self.login_user_context(self.get_superuser()):
            response = self.client.get(self.get_admin_url(ContentExpiry, "changelist"))

        # content_expiry_6 is not shown because it is after the 30 days
        self.assertQuerysetEqual(
            response.context["cl"].queryset,
            [content_expiry_1.pk, content_expiry_2.pk, content_expiry_3.pk,
             content_expiry_4.pk, content_expiry_5.pk],
            transform=lambda x: x.pk,
            ordered=False,
        )

    def test_expired_filter_view_overdue_boundaries(self):
        self.assertSetEqual("TODO: The filter should only show records that are overdue, add values to check the boundaries", "")
