from dateutil.relativedelta import relativedelta
from functools import reduce

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from polymorphic.utils import get_base_polymorphic_model

from .admin import ContentTypeFilter
from .conf import DEFAULT_CONTENT_EXPIRY_DURATION
from .models import DefaultContentExpiryConfiguration


# FIXME: Due to time constraints this function is not covered by unit tests
def _get_version_content_model_content_type(version):
    """
    Returns a content type that describes the content, this is especially
    important for polymorphic models which would otherwise return the wrong content type!
    """
    # If the version identifies as a different content type, be sure to use it
    if hasattr(version.content, "polymorphic_ctype"):
        return version.content.polymorphic_ctype
    # Otherwise, use the content type registered by the version
    return version.content_type


def get_default_duration_for_version(version):
    """
    Returns a default expiration value dependant on whether an entry exists for
    a content type in DefaultContentExpiryConfiguration.
    """
    content_type = _get_version_content_model_content_type(version)
    default_configuration = DefaultContentExpiryConfiguration.objects.filter(
        content_type=content_type
    )
    if default_configuration:
        return relativedelta(months=default_configuration[0].duration)
    return relativedelta(months=DEFAULT_CONTENT_EXPIRY_DURATION)


def get_future_expire_date(version, date):
    """
    Returns a date that will expire after a default period that can differ per content type
    """
    return date + get_default_duration_for_version(version)


def _filter_content_type_polymorphic_content(request, queryset):
    """

    """
    content_types = request.GET.get(ContentTypeFilter.parameter_name)

    if not content_types:
        return queryset

    filters = []
    for content_type in content_types.split(','):
        # Sanitize the value input by the user before using it anywhere
        content_type = int(content_type)
        content_type_obj = ContentType.objects.get_for_id(content_type)
        content_type_model = content_type_obj.model_class()

        # Handle any complex polymorphic models
        if hasattr(content_type_model, "polymorphic_ctype"):
            # Ideally we would reverse query like so, this is sadly not possible due to limitations
            # in django polymorphic. The reverse capability is removed by adding + to the ctype foreign key :-(
            # If polymorphic ever includes a reverse query capability this is all that is eeded
            # related_query_name = f"{content_type_model._meta.app_label}_{content_type_model._meta.model_name}"
            # filters.append(Q(**{
            #     f"version__{related_query_name}__polymorphic_ctype": content_type_obj,
            # }))

            # Get all objects for the base model and then filter by the polymorphic content type
            content_type_inclusion_list = []
            base_content_model = get_base_polymorphic_model(content_type_model)
            base_content_type = ContentType.objects.get_for_model(base_content_model)

            for expiry_record in queryset.filter(version__content_type=base_content_type):
                content = expiry_record.version.content
                # If the record's polymorphic content type matches the selected content type include it.
                if content.polymorphic_ctype_id == content_type_obj.pk:
                    content_type_inclusion_list.append(expiry_record.id)

            filters.append(Q(id__in=content_type_inclusion_list))

    if filters:
        return queryset.filter(reduce(lambda x, y: x | y, filters))

    return queryset