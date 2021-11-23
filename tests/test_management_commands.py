from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase


class CreateExpiryRecordsTestCase(TestCase):

    def test_basic_command_output(self):
        """
        The command should provide messages to the user when starting and when it is finished,
        """
        out = StringIO()

        call_command("create_existing_versions_expiry_records", stdout=out)

        self.assertIn(
            "Starting djangocms_content_expiry.management.commands.create_existing_versions_expiry_records",
            out.getvalue()
        )
        self.assertIn(
            "Finished djangocms_content_expiry.management.commands.create_existing_versions_expiry_records",
            out.getvalue()
        )

    def test_date_options_valid_date_default_format(self):
        date = "2100-02-22"
        out = StringIO()

        call_command(
            "create_existing_versions_expiry_records",
            expiry_date=date,
            stdout=out,
        )

        self.assertIn(
            f"Formatting user supplied date: {date} using the format: %Y-%m-%d",
            out.getvalue()
        )

    def test_date_options_invalid_date_default_format(self):
        date = "210-02-22"
        out = StringIO()

        with self.assertRaisesMessage(CommandError, f"This is an incorrect date string: {date} for the format: %Y-%m-%d"):

            call_command(
                "create_existing_versions_expiry_records",
                expiry_date=date,
                stdout=out,
            )

    def test_date_options_valid_date_supplied_format(self):
        date = "22022100"
        date_format = "%d%m%Y"
        out = StringIO()

        call_command(
            "create_existing_versions_expiry_records",
            expiry_date=date,
            expiry_date_format=date_format,
            stdout=out,
        )

        self.assertIn(
            f"Formatting user supplied date: {date} using the format: {date_format}",
            out.getvalue()
        )

    def test_date_options_invalid_date_supplied_format(self):
        date = "210-02-22"
        date_format = "%d%m%Y"
        out = StringIO()

        with self.assertRaisesMessage(CommandError, f"This is an incorrect date string: {date} for the format: {date_format}"):

            call_command(
                "create_existing_versions_expiry_records",
                expiry_date=date,
                expiry_date_format=date_format,
                stdout=out,
            )

