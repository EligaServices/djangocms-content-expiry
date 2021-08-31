from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string

from djangocms_versioning import admin


def expires(self, obj):
    return render_to_string('djangocms_content_expiry/admin/expiry_date_icon.html')


expires.short_description = _('expire date')
admin.VersionAdmin.expire = expires


def get_list_display(func):
    """
    Register the expire field with the Versioning Admin
    """

    def inner(self, request):
        list_display = func(self, request)
        created_by_index = list_display.index('created_by')
        return list_display[:created_by_index] + ('expire',) + list_display[created_by_index:]

    return inner


admin.VersionAdmin.get_list_display = get_list_display(admin.VersionAdmin.get_list_display)
