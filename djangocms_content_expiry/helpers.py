from django.contrib.auth import get_user_model

from djangocms_content_expiry.models import ContentExpiry


def get_authors():
    """
    Helper to return all authors created by content expiry
    """
    User = get_user_model()
    return User.objects.filter(contentexpiry__created_by__isnull=False).distinct()


def create_version_expiry(version):
    """
    Helper to create a new entry in versioning with the expiration date
    """
    ContentExpiry.objects.filter(version=version).delete()
    ContentExpiry.objects.get_or_create(
        version=version,
        created=version.created,
        created_by=version.created_by,
        expires="2021-09-01 05:48:44.415374-05"
    )
    return version
