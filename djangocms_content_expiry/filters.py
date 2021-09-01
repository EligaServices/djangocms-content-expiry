from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from djangocms_versioning.constants import VERSION_STATES, PUBLISHED
from djangocms_versioning.versionables import _cms_extension

from . import helpers


class ContentTypeFilter(admin.SimpleListFilter):
    title = _("Content Type")
    parameter_name = "content_type"
    template = 'djangocms_content_expiry/multiselect-filter.html'

    def lookups(self, request, model_admin):
        list = []
        for content_type in _cms_extension().versionables_by_content:
            value = ContentType.objects.get_for_model(content_type)
            list.append((value.pk, value))
        return list

    def queryset(self, request, queryset):
        content_type = self.value()
        if not content_type:
            return queryset
        return queryset.filter(version__content_type__in=content_type.split(','))

    def value_as_list(self):
        return self.value().split(',') if self.value() else []

    def _update_query(self, changelist, include=None, exclude=None):
        selected_list = self.value_as_list()
        if include and include not in selected_list:
            selected_list.append(include)
        if exclude and exclude in selected_list:
            selected_list.remove(exclude)
        if selected_list:
            compiled_selection = ','.join(selected_list)
            return changelist.get_query_string({self.parameter_name: compiled_selection})
        else:
            return changelist.get_query_string(remove=[self.parameter_name])

    def choices(self, changelist):
        yield {
            'selected': self.value() is None,
            'query_string': changelist.get_query_string(remove=[self.parameter_name]),
            'display': 'All',
            'initial': True,
        }
        for lookup, title in self.lookup_choices:
            yield {
                'selected': str(lookup) in self.value_as_list(),
                'query_string': changelist.get_query_string({self.parameter_name: lookup}),
                'include_query_string': self._update_query(changelist, include=str(lookup)),
                'exclude_query_string': self._update_query(changelist, exclude=str(lookup)),
                'display': title,
            }


class VersionStateFilter(admin.SimpleListFilter):
    title = _("Version State")
    parameter_name = "state"
    default_filter_value = PUBLISHED
    template = 'djangocms_content_expiry/multiselect-filter.html'

    class Media:
        css = {
            'all': ('css/admin/new_css.css',)
        }

    def _is_default(self, filter_value):
        if self.default_filter_value == filter_value and self.value() is None:
            return True
        return False

    def lookups(self, request, model_admin):
        return VERSION_STATES

    def queryset(self, request, queryset):
        state = self.value()
        if state:
            return queryset.filter(version__state=state)
        return queryset

    def value_as_list(self):
        return self.value().split(',') if self.value() else []

    def _update_query(self, changelist, include=None, exclude=None):
        selected_list = self.value_as_list()
        if include and include not in selected_list:
            selected_list.append(include)
        if exclude and exclude in selected_list:
            selected_list.remove(exclude)
        if selected_list:
            compiled_selection = ','.join(selected_list)
            return changelist.get_query_string({self.parameter_name: compiled_selection})
        else:
            return changelist.get_query_string(remove=[self.parameter_name])

    def choices(self, changelist):
        yield {
            "selected": self.value() is None,
            "query_string": changelist.get_query_string(remove=[self.parameter_name]),
            "display": _("All"),
        }
        for lookup, title in self.lookup_choices:
            lookup_value = str(lookup)
            yield {
                "selected": self.value() == lookup_value or self._is_default(lookup_value),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}
                ),
                'include_query_string': self._update_query(changelist, include=str(lookup_value)),
                'exclude_query_string': self._update_query(changelist, exclude=str(lookup_value)),
                "display": title,
            }


class AuthorFilter(admin.SimpleListFilter):
    """
    An author filter limited to those users who have added expiration dates
    """
    title = _("Author")
    parameter_name = "created_by"

    def lookups(self, request, model_admin):
        from django.utils.encoding import force_text
        options = []
        for user in helpers.get_authors():
            options.append(
                (force_text(user.pk), user.get_full_name() or user.get_username())
            )
        return options

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(created_by=self.value()).distinct()
        return queryset
