from django.conf import settings

from cms.app_base import CMSAppConfig

from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html


def _get_moderation_content_expiry_link(obj, request):
    """
    Return a user friendly button for viewing content expiry in djangocms-moderation
    :param obj: TODO
    :return: TODO
    """
    version = obj.moderation_request.version

    # If a content expiry record exists we can go to it
    if hasattr(version, "contentexpiry"):
        view_endpoint = format_html(
            "{}?collection__id__exact={}",
            reverse("admin:djangocms_content_expiry_contentexpiry_change", args=[version.contentexpiry.id]),
            obj.pk,
        )
        return render_to_string(
            "djangocms_content_expiry/calendar_icon.html", {"url": view_endpoint}
        )
    # Otherwise we need to be able to create a new content expiry record
    add_endpoint = reverse('admin:djangocms_content_expiry_contentexpiry_add')
    compiled_add_endpoint = f"{add_endpoint}?version={version.pk}&created_by={request.user.pk}"
    return render_to_string(
        "djangocms_content_expiry/calendar_plus_icon.html", {"url": compiled_add_endpoint}
    )


class ContentExpiryAppConfig(CMSAppConfig):
    # Enable moderation to be able to "configure it"
    djangocms_moderation_enabled = True
    moderated_models = []
    moderation_collection_admin_actions = [_get_moderation_content_expiry_link]
    # Enable versioning because moderation is versioning dependant
    djangocms_versioning_enabled = True
    versioning = []

    djangocms_content_expiry_enabled = getattr(
        settings, "DJANGOCMS_CONTENT_EXPIRY_ENABLED", True
    )
