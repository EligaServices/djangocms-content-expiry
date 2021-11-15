import csv
import datetime

from django.apps import apps
from django.conf.urls import url
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html_join
from django.utils.translation import ugettext_lazy as _

from djangocms_versioning.constants import PUBLISHED
from djangocms_versioning.helpers import get_preview_url

from .conf import DEFAULT_CONTENT_EXPIRY_EXPORT_DATE_FORMAT
from .filters import (
    AuthorFilter,
    ContentExpiryDateRangeFilter,
    ContentTypeFilter,
    VersionStateFilter,
)
from .forms import ContentExpiryForm, DefaultContentExpiryConfigurationForm
from .helpers import get_rangefilter_expires_default
from .models import ContentExpiry, DefaultContentExpiryConfiguration



from functools import reduce

from django.db.models import Q

from polymorphic.utils import get_base_polymorphic_model


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

@admin.register(ContentExpiry)
class ContentExpiryAdmin(admin.ModelAdmin):
    list_display = ['title', 'content_type', 'expires', 'version_state', 'version_author']
    list_display_links = None
    list_filter = (ContentTypeFilter, ('expires', ContentExpiryDateRangeFilter), VersionStateFilter, AuthorFilter)
    form = ContentExpiryForm
    change_list_template = "djangocms_content_expiry/admin/change_list.html"

    class Media:
        css = {
            'all': (
                'djangocms_content_expiry/css/actions.css',
                'djangocms_content_expiry/css/date_filter.css',
                'djangocms_content_expiry/css/multiselect_filter.css',
            )
        }

    def get_search_results(self, request, queryset, search_term):
        queryset, may_have_duplicates = super().get_search_results(
            request, queryset, search_term,
        )

        # Handle custom Content Type filters for Polymorphic models!
        # Only filter by
        queryset = _filter_content_type_polymorphic_content(request, queryset)

        return queryset, may_have_duplicates

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        # Execute any filters that need to be added before any of the admin filters
        # are executed
        app_config = apps.get_app_config("djangocms_content_expiry")
        for content_model_filter in app_config.cms_extension.expiry_changelist_queryset_filters:
            queryset = content_model_filter(queryset, request=request)

        return queryset

    def has_add_permission(self, *args, **kwargs):
        # Entries are added automatically
        return False

    def has_delete_permission(self, *args, **kwargs):
        # Deletion should never be possible, the only way that a
        # content expiry record could be deleted is via versioning.
        return False

    def get_list_display(self, request):
        return [
            "title",
            "content_type",
            "expires",
            "version_state",
            "version_author",
            self.list_display_actions(request),
        ]

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        return [
            url(
                r'^export_csv/$',
                self.admin_site.admin_view(self.export_to_csv),
                name="{}_{}_export_csv".format(*info),
            ),
        ] + super().get_urls()

    def get_rangefilter_expires_default(self, *args, **kwargs):
        return get_rangefilter_expires_default()

    def get_rangefilter_expires_title(self, *args, **kwargs):
        return _("By Expiry Date Range")

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

    def list_display_actions(self, request):
        """
        A closure that makes it possible to pass request object to
        list action button functions.

        :param request: a request object
        :returns: A callable for the changelist to render icons
        """
        actions = [
            self._get_preview_link,
            self._get_edit_link,
        ]

        def list_actions(obj):
            """
            Display links to state change endpoints
            """
            return format_html_join(
                "", "{}", ((action(obj, request),) for action in actions)
            )

        list_actions.short_description = _("actions")
        return list_actions

    def _get_preview_url(self, obj):
        """
        Find a valid preview url for a content object.

        :param obj: this is a content expiry object
        :returns: A valid preview url to link to the content object
        """
        content_obj = obj.version.content
        # If the version is published, first try and get a "live" url
        if obj.version.state == PUBLISHED:
            if hasattr(content_obj, "get_absolute_url"):
                return content_obj.get_absolute_url()
        # If the content object has a preview url, get it
        if hasattr(content_obj, "get_preview_url"):
            return content_obj.get_preview_url()
        # Otherwise, all else has failed, try and get a preview url
        return get_preview_url(content_obj)

    def _get_preview_link(self, obj, request):
        """
        Build a link to preview the content object from the supplied content object.

        :param obj: A content expiry object
        :param request: A request object
        :returns: An edit link to the supplied content expiry record
        """
        preview_url = self._get_preview_url(obj)

        return render_to_string(
            "djangocms_content_expiry/admin/icons/preview_action_icon.html", {
                "url": preview_url,
            }
        )

    def _get_edit_link(self, obj, request):
        """
        Build a link to edit the content expiry object.

        :param obj: A content expiry object
        :param request: A request object
        :returns: An edit link to the supplied content expiry record
        """
        archive_url = reverse(
            "admin:{app}_{model}_change".format(
                app=obj._meta.app_label, model=self.model._meta.model_name
            ),
            args=(obj.pk,),
        )

        return render_to_string(
            "djangocms_content_expiry/admin/icons/edit_action_icon.html", {
                "url": archive_url,
            }
        )

    def _format_export_datetime(self, date, date_format=DEFAULT_CONTENT_EXPIRY_EXPORT_DATE_FORMAT):
        """
        Format a supplied date object.

        :param date: DateTime object
        :param date_format: String, date time string format for strftime
        :returns: A formatted human readable date time string
        """
        if isinstance(date, datetime.date):
            return date.strftime(date_format)
        return ""

    def export_to_csv(self, request):
        """
        Retrieves the queryset and exports to csv format
        """
        queryset = self.get_exported_queryset(request)
        meta = self.model._meta
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        # Write the header to the file
        writer.writerow([
            'Title',
            'Content Type',
            'Expiry Date',
            'Version State',
            'Version Author',
            'Url'
        ])

        for content_expiry in queryset:
            content_type = ContentType.objects.get_for_model(content_expiry.version.content)
            expiry_date = self._format_export_datetime(content_expiry.expires)
            version_state = content_expiry.version.get_state_display()
            # Get an external / sharable link
            preview_url = self._get_preview_url(content_expiry)
            external_url = request.build_absolute_uri(preview_url)
            # Write a row to the file
            writer.writerow([
                content_expiry.version.content,
                content_type,
                expiry_date,
                version_state,
                content_expiry.version.created_by,
                external_url,
            ])

        return response

    def get_exported_queryset(self, request):
        """
        Returns export queryset by respecting applied filters.
        """
        list_display = self.get_list_display(request)
        list_display_links = self.get_list_display_links(request, list_display)
        list_filter = self.get_list_filter(request)
        search_fields = self.get_search_fields(request)
        changelist = self.get_changelist(request)

        changelist_kwargs = {
            'request': request,
            'model': self.model,
            'list_display': list_display,
            'list_display_links': list_display_links,
            'list_filter': list_filter,
            'date_hierarchy': self.date_hierarchy,
            'search_fields': search_fields,
            'list_select_related': self.list_select_related,
            'list_per_page': self.list_per_page,
            'list_max_show_all': self.list_max_show_all,
            'list_editable': self.list_editable,
            'model_admin': self,
            'sortable_by': self.sortable_by
        }
        cl = changelist(**changelist_kwargs)

        return cl.get_queryset(request)


@admin.register(DefaultContentExpiryConfiguration)
class DefaultContentExpiryConfigurationAdmin(admin.ModelAdmin):
    list_display = ['content_type', 'duration']
    form = DefaultContentExpiryConfigurationForm
