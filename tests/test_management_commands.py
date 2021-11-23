from datetime import datetime
from io import StringIO
import factory

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from cms.test_utils.testcases import CMSTestCase

from djangocms_versioning.models import Version
from djangocms_versioning.signals import post_version_operation, pre_version_operation

from djangocms_content_expiry.test_utils.polls.factories import PollVersionFactory
from djangocms_content_expiry.test_utils.polymorphic_project.factories import ProjectContentVersionFactory


class CreateExpiryRecordsTestCase(TestCase):

    def setUp(self):
        self.out = StringIO()

    def test_basic_command_output(self):
        """
        The command should provide messages to the user when starting and when it is finished,
        """
        call_command("create_existing_versions_expiry_records", stdout=self.out)

        self.assertIn(
            "Starting djangocms_content_expiry.management.commands.create_existing_versions_expiry_records",
            self.out.getvalue()
        )
        self.assertIn(
            "Finished djangocms_content_expiry.management.commands.create_existing_versions_expiry_records",
            self.out.getvalue()
        )

    def test_date_options_valid_date_default_format(self):
        date = "2100-02-22"

        call_command(
            "create_existing_versions_expiry_records",
            expiry_date=date,
            stdout=self.out,
        )

        self.assertIn(
            f"Formatting user supplied date: {date} using the format: %Y-%m-%d",
            self.out.getvalue()
        )

    def test_date_options_invalid_date_default_format(self):
        date = "210-02-22"

        with self.assertRaisesMessage(CommandError, f"This is an incorrect date string: {date} for the format: %Y-%m-%d"):

            call_command(
                "create_existing_versions_expiry_records",
                expiry_date=date,
                stdout=self.out,
            )

    def test_date_options_valid_date_supplied_format(self):
        date = "22022100"
        date_format = "%d%m%Y"

        call_command(
            "create_existing_versions_expiry_records",
            expiry_date=date,
            expiry_date_format=date_format,
            stdout=self.out,
        )

        self.assertIn(
            f"Formatting user supplied date: {date} using the format: {date_format}",
            self.out.getvalue()
        )

    def test_date_options_invalid_date_supplied_format(self):
        date = "210-02-22"
        date_format = "%d%m%Y"

        with self.assertRaisesMessage(CommandError, f"This is an incorrect date string: {date} for the format: {date_format}"):

            call_command(
                "create_existing_versions_expiry_records",
                expiry_date=date,
                expiry_date_format=date_format,
                stdout=self.out,
            )


class CreateExpiryRecordsDateOverrideTestCase(CMSTestCase):

    @factory.django.mute_signals(pre_version_operation, post_version_operation)
    def setUp(self):
        self.out = StringIO()

        poll_content_versions = PollVersionFactory.create_batch(5, content__language="en")
        project_content_versions = ProjectContentVersionFactory.create_batch(5)

        # A sanity check to ensure that the models don't have expiry records attached!
        self.assertFalse(hasattr(poll_content_versions[0], "contentexpiry"))
        self.assertFalse(hasattr(project_content_versions[0], "contentexpiry"))

    def test_option_one(self):

        call_command(
            "create_existing_versions_expiry_records",
            stdout=self.out,
        )

        versions = Version.objects.all()

        self.assertEqual(len(versions), 10)

        for version in versions:
            self.assertEqual(version.contentexpiry.expires, "")

    def test_option_two(self):
        date = "2100-02-22"
        date_format = "%Y-%m-%d"

        call_command(
            "create_existing_versions_expiry_records",
            expiry_date=date,
            expiry_date_format=date_format,
            stdout=self.out,
        )

        versions = Version.objects.all()

        self.assertEqual(len(versions), 10)

        for version in versions:
            expected_date = datetime.strptime(date, date_format)

            self.assertEqual(version.contentexpiry.expires, expected_date)
