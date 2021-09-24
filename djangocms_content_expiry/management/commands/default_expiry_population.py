from django.core.management.base import BaseCommand

from djangocms_versioning.models import Version

from djangocms_content_expiry.models import ContentExpiry
from djangocms_content_expiry.utils import get_default_duration_for_version


class Command(BaseCommand):
    help = 'Creates Default Content Expiry entries'

    def _populate_existing_version_content_expiry_records(self):

        for version in Version.objects.filter(contentexpiry__isnull=True):
            duration = get_default_duration_for_version(version)
            expiry_date = version.created + duration

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
