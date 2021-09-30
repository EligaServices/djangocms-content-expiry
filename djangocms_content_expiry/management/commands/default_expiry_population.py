from django.core.management.base import BaseCommand

from djangocms_versioning.models import Version

from djangocms_content_expiry.models import ContentExpiry
from djangocms_content_expiry.utils import get_future_expire_date


class Command(BaseCommand):
    help = 'Creates Default Content Expiry entries'

    def _populate_existing_version_content_expiry_records(self):
        """
        Create any content expiry records for versions in the system
        """
        for version in Version.objects.filter(contentexpiry__isnull=True):
            # Use the modified date because this is the date that a published
            # version was published which is what really matters for Expired content!
            expiry_date = get_future_expire_date(version, version.modified)

            ContentExpiry.objects.create(
                created_by=version.created_by,
                version=version,
                expires=expiry_date,
            )

            self.stdout.write(
                f"Content Expiry created for version: {version}")

    def handle(self, *args, **options):
        self.stdout.write(f"Starting {__name__}")

        self._populate_existing_version_content_expiry_records()

        self.stdout.write(self.style.SUCCESS(f"Finished {__name__}"))
