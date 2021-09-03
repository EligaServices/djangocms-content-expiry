from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

import datetime

from djangocms_versioning.constants import PUBLISHED, VERSION_STATES
from djangocms_versioning.versionables import _cms_extension

from rangefilter.filters import DateRangeFilter

from . import helpers


class SimpleListMultiselectFilter(admin.SimpleListFilter):

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


class ContentTypeFilter(SimpleListMultiselectFilter):
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


class VersionStateFilter(SimpleListMultiselectFilter):
    title = _("Version State")
    parameter_name = "state"
    default_filter_value = PUBLISHED
    show_all_param_value = "_all_"
    template = 'djangocms_content_expiry/multiselect-filter.html'

    def _is_default(self, filter_value):
        if self.default_filter_value == filter_value and self.value() is None:
            return True
        return False

    def _get_all_query_string(self, changelist):
        """
        If there's a default value set the all parameter needs to be provided
        however, if a default is not set the all parameter is not required.
        """
        # Default setting in use
        if self.default_filter_value:
            return changelist.get_query_string(
                {self.parameter_name:  self.show_all_param_value}
            )
        # Default setting not in use
        return changelist.get_query_string(remove=[self.parameter_name])

    def _is_all_selected(self):
        state = self.value()
        # Default setting in use
        if self.default_filter_value and state == self.show_all_param_value:
            return True
        # Default setting not in use
        elif not self.default_filter_value and not state:
            return True
        return False

    def _update_query(self, changelist, include=None, exclude=None):
        selected_list = self.value_as_list()

        if self.show_all_param_value in selected_list:
            selected_list.remove(self.show_all_param_value)

        if include and include not in selected_list:
            selected_list.append(include)
        if exclude and exclude in selected_list:
            selected_list.remove(exclude)
        if selected_list:
            compiled_selection = ','.join(selected_list)
            return changelist.get_query_string({self.parameter_name: compiled_selection})
        else:
            return changelist.get_query_string(remove=[self.parameter_name])

    def lookups(self, request, model_admin):
        return VERSION_STATES

    def queryset(self, request, queryset):
        state = self.value()
        # Default setting in use
        if self.default_filter_value:
            if not state:
                return queryset.filter(version__state=self.default_filter_value)
            elif state != "_all_":
                return queryset.filter(version__state__in=state.split(','))
        # Default setting not in use
        elif not self.default_filter_value and state:
            return queryset.filter(version__state__in=state.split(','))
        return queryset

    def choices(self, changelist):
        yield {
            "selected": self._is_all_selected(),
            "query_string": self._get_all_query_string(changelist),
            "display": _("All"),
            'initial': True,
        }
        for lookup, title in self.lookup_choices:
            lookup_value = str(lookup)
            yield {
                "selected":  str(lookup) in self.value_as_list() or self._is_default(lookup_value),
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


class CustomDateRangeFilter(DateRangeFilter):
    """
    Custom date range filter limited to default values set in date range filter
    """
    def _make_query_filter(self, request, validated_data):
        """
        Override the _make_query_filter method to enforce a default setting being loaded by default
        """
        query_params = super()._make_query_filter(request, validated_data)

        if not self.default_gte or not self.default_lte:
            return query_params

        date_value_gte = validated_data.get(self.lookup_kwarg_gte, None)
        date_value_lte = validated_data.get(self.lookup_kwarg_lte, None)
        if not date_value_gte and not date_value_lte:
            query_params['{0}__gte'.format(self.field_path)] = self.make_dt_aware(
                datetime.datetime.combine(self.default_gte, datetime.time.min),
                self.get_timezone(request),
            )
            query_params['{0}__lte'.format(self.field_path)] = self.make_dt_aware(
                datetime.datetime.combine(self.default_lte, datetime.time.max),
                self.get_timezone(request),
            )
        return query_params