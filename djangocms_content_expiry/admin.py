from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from rangefilter.filters import DateRangeFilter

from .filters import ContentTypeFilter, VersionStateFilter, AuthorFilter
from .models import ContentExpiry


@admin.register(ContentExpiry)
class ContentExpiryAdmin(admin.ModelAdmin):
    list_display = ['title', 'content_type', 'expires', 'version_state', 'version_author']
    # Disable automatically linking to the Expiry record
    list_display_links = None
    list_filter = (ContentTypeFilter, ('expires', DateRangeFilter), VersionStateFilter, AuthorFilter)

    class Media:
        css = {
            'all': ('css/date_filter.css',)
        }

    def title(self, obj):
        """
        A field to display the content objects title
        """
        return obj.version.content
    title.short_description = _('Title')

    def content_type(self, obj):
        """
        A field to display the content type as a readable representation
        """
        return ContentType.objects.get_for_model(
            obj.version.content
        )
    content_type.short_description = _('Content type')

    def version_state(self, obj):
        """
        A field to display the version state as a readable representation
        """
        return obj.version.get_state_display()
    version_state.short_description = _('Version state')

    def version_author(self, obj):
        """
        A field to display the author of the version
        """
        return obj.version.created_by
    version_author.short_description = _('Version author')
