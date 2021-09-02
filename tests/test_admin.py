from cms.test_utils.testcases import CMSTestCase

import datetime
from unittest import skip

from djangocms_content_expiry.models import ContentExpiry
from djangocms_content_expiry.test_utils.factories import ContentExpiryFactory
from djangocms_content_expiry.test_utils.polls.factories import (
    PollContentWithVersionFactory,
)


class ContentExpiryChangelistTestCase(CMSTestCase):
    def test_changelist_form_fields(self):
        """
        Ensure that the form fields present match the model fields"
        """
        with self.login_user_context(self.get_superuser()):
            response = self.client.get(self.get_admin_url(ContentExpiry, "add"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 200)

        decoded_response = response.content.decode("utf-8")

        self.assertIn('<select name="created_by" required id="id_created_by">', decoded_response)
        self.assertIn('<select name="version" required id="id_version">', decoded_response)
        self.assertIn('<input type="text" name="expires_0" class="vDateField" size="10" required id="id_expires_0">',
                      decoded_response)

    def test_change_fields(self):
        """
        Ensure the change list presents list display items from the admin file
        """
        with self.login_user_context(self.get_superuser()):
            response = self.client.get(self.get_admin_url(ContentExpiry, "changelist"))

        context = response.context_data['cl'].list_display
        self.assertEqual('title', context[1])
        self.assertEqual('content_type', context[2])
        self.assertEqual('expires', context[3])
        self.assertEqual('version_state', context[4])
        self.assertEqual('version_author', context[5])


class ContentExpiryChangelistExpiryFilterTestCase(CMSTestCase):

    @skip("FIXME: TBD")
    def test_expired_filter_default_setting(self):
        self.assertSetEqual("TODO: The is_default settings should be tested and enforced", "")

    def test_expired_filter_setting_expired_at_range_boundaries(self):
        """
        Check the boundaries of the Expired by date range filter. The dates are
        set to check that only records due to expire are shown with a filter value set at 30 days
        """
        from_date = datetime.datetime.now()
        to_date = from_date + datetime.timedelta(days=30)

        # Record that is expired by 1 day
        delta_1 = datetime.timedelta(days=1)
        expire_at_1 = from_date - delta_1
        poll_content_1 = PollContentWithVersionFactory(language="en")
        content_expiry_1 = ContentExpiryFactory(version=poll_content_1.versions.first(), expires=expire_at_1)

        # Record that is set to expire today
        expire_at_2 = from_date
        poll_content_2 = PollContentWithVersionFactory(language="en")
        content_expiry_2 = ContentExpiryFactory(version=poll_content_2.versions.first(), expires=expire_at_2)

        # Record that is set to expire tomorrow
        delta_3 = datetime.timedelta(days=1)
        expire_at_3 = from_date + delta_3
        poll_content_3 = PollContentWithVersionFactory(language="en")
        content_expiry_3 = ContentExpiryFactory(version=poll_content_3.versions.first(), expires=expire_at_3)

        # Record that is set to expire in 29 days
        delta_4 = datetime.timedelta(days=29)
        expire_at_4 = from_date + delta_4
        poll_content_4 = PollContentWithVersionFactory(language="en")
        content_expiry_4 = ContentExpiryFactory(version=poll_content_4.versions.first(), expires=expire_at_4)

        # Record that is set to expire in 30 days
        delta_5 = datetime.timedelta(days=30)
        expire_at_5 = from_date + delta_5
        poll_content_5 = PollContentWithVersionFactory(language="en")
        content_expiry_5 = ContentExpiryFactory(version=poll_content_5.versions.first(), expires=expire_at_5)

        # Record that is set to expire in 31 days
        delta_6 = datetime.timedelta(days=31)
        expire_at_6 = from_date + delta_6
        poll_content_6 = PollContentWithVersionFactory(language="en")
        ContentExpiryFactory(version=poll_content_6.versions.first(), expires=expire_at_6)

        with self.login_user_context(self.get_superuser()):
            url_date_range = f"?expires__range__gte={from_date.date()}&expires__range__lte={to_date.date()}"
            admin_endpoint = self.get_admin_url(ContentExpiry, "changelist")
            response = self.client.get(admin_endpoint + url_date_range)

        # content_expiry_1 and content_expiry_6 are not shown because they are outside of the set
        # boundary range, content_expiry_1 is before the start and content_expiry_6 is outside of the range.
        self.assertQuerysetEqual(
            response.context["cl"].queryset,
            [content_expiry_2.pk, content_expiry_3.pk,
             content_expiry_4.pk, content_expiry_5.pk],
            transform=lambda x: x.pk,
            ordered=False,
        )

    def test_expired_filter_published_always_filtered(self):
        """
        All published items should never be shown to the user as they have been expired and acted on
        """
        delta = datetime.timedelta(days=31)
        expire = datetime.datetime.now() + delta
        poll_content = PollContentWithVersionFactory(language="en")
        ContentExpiryFactory(version=poll_content.versions.first(), expires=expire)

        with self.login_user_context(self.get_superuser()):
            response = self.client.get(self.get_admin_url(ContentExpiry, "changelist"))

        published_query_set = response.context["cl"].queryset.filter(version__state="published")

        self.assertEqual(len(published_query_set), 0)

    def test_author_filter(self):
        """
        Author filter should only show selected author's results
        """
        delta1 = datetime.timedelta(days=31)
        expire1 = datetime.datetime.now() + delta1
        poll_content1 = PollContentWithVersionFactory(language="en")
        expiry_object1 = ContentExpiryFactory(version=poll_content1.versions.first(), expires=expire1)

        delta2 = datetime.timedelta(days=31)
        expire2 = datetime.datetime.now() + delta2
        poll_content2 = PollContentWithVersionFactory(language="en")
        expiry_object2 = ContentExpiryFactory(version=poll_content2.versions.first(), expires=expire2)

        with self.login_user_context(self.get_superuser()):
            response = self.client.get(self.get_admin_url(ContentExpiry, "changelist"))

        # Query count should only show expiry_object1 as it should match the author selected
        published_query_set = response.context["cl"].queryset.filter(created_by=expiry_object1.created_by)

        self.assertEqual(len(published_query_set), 1)
