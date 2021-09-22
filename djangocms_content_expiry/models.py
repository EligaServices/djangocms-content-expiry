from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from djangocms_versioning.models import Version


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
    expires = models.DateTimeField(_("expiry date"))

    class Meta:
        verbose_name = _("Content Expiry")
        verbose_name_plural = _("Content Expiry")


from djangocms_versioning.versionables import _cms_extension

def limit_pub_date_choices():
    content_type_choices = []
    for content_type in _cms_extension().versionables_by_content:
        value = ContentType.objects.get_for_model(content_type)
        content_type_choices.append((value.pk, value))
        return content_type_choices


class ContentExpiryContentTypeConfiguration(models.Model):
    duration = models.IntegerField(help_text=_("duration in days"))
    content_type = models.OneToOneField(
        ContentType,
        primary_key=True,
        limit_choices_to=limit_pub_date_choices,
        on_delete=models.CASCADE,
        verbose_name=_('content type')
    )

    class Meta:
        verbose_name = _("Content Type Configuration")
        verbose_name_plural = _("Content Type Configuration")



