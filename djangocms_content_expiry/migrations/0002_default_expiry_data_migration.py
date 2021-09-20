from datetime import datetime, timedelta

from django.db import migrations


def forwards(apps, schema_editor):
    Version = apps.get_model('djangocms_versioning', 'Version')
    ContentExpiry = apps.get_model('djangocms_content_expiry', 'ContentExpiry')

    for version in Version.objects.all():

        expiry_date = timedelta(days=365)
        expiry_date = version.created + expiry_date

        ContentExpiry.objects.create(
            created_by=version.created_by,
            version=version,
            expires=expiry_date,
        )

        print(f"expiry created for version: {version}")


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_content_expiry', '0001_initial'),
        ('djangocms_versioning', '0012_create_version_numbers'),
    ]

    operations = [
        migrations.RunPython(forwards),
    ]
