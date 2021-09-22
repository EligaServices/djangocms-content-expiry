from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from djangocms_versioning.models import Version

from .conf import DEFAULT_CONTENT_EXPIRY_DURATION
from .constants import CONTENT_EXPIRY_EXPIRE_FIELD_LABEL


class ContentExpiry(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name=_('expired by')
    )
    version = models.OneToOneField(
        Version,
        on_delete=models.CASCADE,
        verbose_name=_('version')
    )
    expires = models.DateTimeField(CONTENT_EXPIRY_EXPIRE_FIELD_LABEL)

    class Meta:
        verbose_name = _("Content Expiry")
        verbose_name_plural = _("Content Expiry")


from djangocms_versioning.versionables import _cms_extension


def limit_content_type_choices():
    model_list = [value for value in _cms_extension().versionables_by_content]
    content_type_list = ContentType.objects.get_for_models(*model_list).items()
    inclusion = [content_type.pk for k, content_type in content_type_list]

    existing = ContentExpiryContentTypeConfiguration.objects.filter(
        **{"content_type__in": inclusion}
    ).values_list('pk', flat=True)
    for item in existing:
        inclusion.remove(item)

    return {"id__in": inclusion}


class ContentExpiryContentTypeConfiguration(models.Model):
    content_type = models.OneToOneField(
        ContentType,
        primary_key=True,
        limit_choices_to=limit_content_type_choices,
        on_delete=models.CASCADE,
        verbose_name=_('content type')
    )
    duration = models.IntegerField(help_text=_("Duration in days"), default=DEFAULT_CONTENT_EXPIRY_DURATION)

    class Meta:
        verbose_name = _("Content Type Configuration")
        verbose_name_plural = _("Content Type Configuration")

    def __str__(self):
        return str(self.content_type)
