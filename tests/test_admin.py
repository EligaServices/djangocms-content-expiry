import datetime

from cms.test_utils.testcases import CMSTestCase

from djangocms_content_expiry.models import ContentExpiry
from djangocms_content_expiry.test_utils.factories import ContentExpiryFactory
from djangocms_content_expiry.test_utils.polls.factories import PollContentWithVersionFactory


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

    def test_expired_filter_default_setting(self):
        self.assertSetEqual("TODO: The is_default settings should be tested and enforced", "")

    def test_expired_filter_setting_expired_at_boundaries(self):
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

    def test_expired_filter_setting_overdue_boundaries(self):
        self.assertSetEqual("TODO: The filter should only show records that are overdue, add values to check the boundaries", "")

    def test_expired_filter_published_always_filtered(self):
        """
        All published items should never be shown to the user as they have been expired and acted on
        """
        delta = datetime.timedelta(days=31)
        expire = datetime.datetime.now() + delta
        poll_content_6 = PollContentWithVersionFactory(language="en")
        ContentExpiryFactory(version=poll_content_6.versions.first(), expires=expire)

        with self.login_user_context(self.get_superuser()):
            response = self.client.get(self.get_admin_url(ContentExpiry, "changelist"))
        test = response.context["cl"].queryset

        self.assertEqual(len(test), 1)
