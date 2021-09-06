from django.utils.translation import ugettext_lazy as _

from djangocms_versioning import admin, models

from djangocms_content_expiry.helpers import create_version_expiry
from djangocms_content_expiry.models import ContentExpiry


def expires(self, obj):
    version = ContentExpiry.objects.filter(version=obj.pk)
    if version:
        return version[0].expires
    return ""


expires.short_description = _('expire date')
admin.VersionAdmin.expire = expires


def get_list_display(func):
    """
    Register the locked field with the Versioning Admin
    """

    def inner(self, request):
        list_display = func(self, request)
        created_by_index = list_display.index('created_by')
        return list_display[:created_by_index] + ('expire',) + list_display[created_by_index:]

    return inner


admin.VersionAdmin.get_list_display = get_list_display(admin.VersionAdmin.get_list_display)


# def new_save(old_save):
#     """
#     Override the Versioning save method to add the expiration date
#     """
#     def inner(version, **kwargs):
#         old_save(version, **kwargs)
#         create_version_expiry(version)
#         return version
#     return inner
#
#
# models.Version.save = new_save(models.Version.save)
