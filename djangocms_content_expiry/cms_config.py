from django.conf import settings

from cms.app_base import CMSAppConfig

from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _


def get_moderation_content_expiry_link(obj):
    """
    Return a user friendly button for viewing content expiry in the
    actions section of the Moderation Request Admin Changelist
    in djangocms-moderation.

    :param obj: A Moderation Request object supplied from the admin view table row
    :return: A link to the expiry record if one exists
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
    return ""


def get_expiry_date(obj):
    """
    A custom field to show the expiry date in the
    Moderation Request Admin Changelist in djangocms-moderation.

    :param obj: A Moderation Request object supplied from the admin view table row
    :return: The expiry date from the matching moderation request object
    """
    version = obj.moderation_request.version

    if hasattr(version, "contentexpiry"):
        return version.contentexpiry.expires


get_expiry_date.short_description = _('Expires')


class ContentExpiryAppConfig(CMSAppConfig):
    # Enable moderation to be able to "configure it"
    djangocms_moderation_enabled = True
    moderated_models = []
    moderation_request_changelist_actions = [
        get_moderation_content_expiry_link,
    ]
    moderation_request_changelist_fields = [
        get_expiry_date,
    ]
    # Enable versioning because moderation is versioning dependant
    djangocms_versioning_enabled = True
    versioning = []

    djangocms_content_expiry_enabled = getattr(
        settings, "DJANGOCMS_CONTENT_EXPIRY_ENABLED", True
    )
