from dateutil.relativedelta import relativedelta

from .conf import DEFAULT_CONTENT_EXPIRY_DURATION
from .models import DefaultContentExpiryConfiguration


def get_default_duration_for_version(version):
    default_configuration = DefaultContentExpiryConfiguration.objects.filter(
        content_type=version.content_type
    )
    if default_configuration:
        return relativedelta(months=default_configuration.duration)
    return relativedelta(months=DEFAULT_CONTENT_EXPIRY_DURATION)
