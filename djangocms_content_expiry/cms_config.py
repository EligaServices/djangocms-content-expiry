from django.conf import settings

from cms.app_base import CMSAppConfig

from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _


def _get_moderation_content_expiry_link(obj):
    """
    Return a user friendly button for viewing content expiry in djangocms-moderation
    :param obj: TODO
    :return: TODO
    """
    version = obj.moderation_request.version

    # If a content expiry record exists we can go to it
    if hasattr(version, "contentexpiry"):
        view_endpoint = format_html(
            "{}?collection__id__exact={}&_popup=1",
            reverse("admin:djangocms_content_expiry_contentexpiry_change", args=[version.contentexpiry.pk]),
            obj.pk,
        )
        return render_to_string(
            "djangocms_content_expiry/calendar_icon.html", {"url": view_endpoint, "field_id": f"contentexpiry_{obj.pk}"}
        )


def get_expiry_date(obj):
    """
    A custom field to show the expiry date in the moderation collection
    change list
    """
    version = obj.moderation_request.version

    if hasattr(version, "contentexpiry"):
        return version.contentexpiry.expires
get_expiry_date.short_description = _('Expires')


class ContentExpiryAppConfig(CMSAppConfig):
    # Enable moderation to be able to "configure it"
    djangocms_moderation_enabled = True
    moderated_models = []
    moderation_collection_admin_actions = [_get_moderation_content_expiry_link]
    moderation_collection_admin_fields = [get_expiry_date]
    # Enable versioning because moderation is versioning dependant
    djangocms_versioning_enabled = True
    versioning = []

    djangocms_content_expiry_enabled = getattr(
        settings, "DJANGOCMS_CONTENT_EXPIRY_ENABLED", True
    )
