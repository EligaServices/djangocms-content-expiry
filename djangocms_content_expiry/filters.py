from datetime import datetime, timedelta

from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from djangocms_versioning.constants import VERSION_STATES
from djangocms_versioning.versionables import _cms_extension


class ContentTypeFilter(admin.SimpleListFilter):
    title = _("Content Type")
    parameter_name = "content_type"

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
        return queryset.filter(version__content_type=content_type)

    def choices(self, changelist):
        yield {
            "selected": self.value() is None,
            "query_string": changelist.get_query_string(remove=[self.parameter_name]),
            "display": _("All"),
        }
        for lookup, title in self.lookup_choices:
            yield {
                "selected": self.value() == str(lookup),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}
                ),
                "display": title,
            }


class VersionStateFilter(admin.SimpleListFilter):
    title = _("Version State")
    parameter_name = "state"

    def lookups(self, request, model_admin):
        return VERSION_STATES

    def queryset(self, request, queryset):
        state = self.value()
        if state:
            return queryset.filter(version__state=state)
        return queryset

    def choices(self, changelist):
        yield {
            "selected": self.value() is None,
            "query_string": changelist.get_query_string(remove=[self.parameter_name]),
            "display": _("All"),
        }
        for lookup, title in self.lookup_choices:
            yield {
                "selected": self.value() == str(lookup),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}
                ),
                "display": title,
            }


# TODO: Move to conf.py driven by settings or constants.py if not driven by settings!
# https://github.com/django-cms/djangocms-moderation/blob/release/1.0.x/djangocms_moderation/conf.py
# https://github.com/django-cms/djangocms-moderation/blob/release/1.0.x/djangocms_moderation/constants.py
DAYS = 30
DUE_TO_EXPIRE = "due_to_expire"
OVERDUE = "overdue"
FILTER_DEFAULT = DUE_TO_EXPIRE


class ExpiredFilter(admin.SimpleListFilter):
    title = _("Expiry Date")
    parameter_name = "expiry"
    default_filter_value = FILTER_DEFAULT

    def _is_default(self, filter_value):
        if self.default_filter_value == filter_value and self.value() is None:
            return True
        return False

    def lookups(self, request, model_admin):
        return [
            (DUE_TO_EXPIRE, f"Due in {DAYS} days"),
            (OVERDUE, "Overdue"),
        ]

    def queryset(self, request, queryset):
        date_from = datetime.now()

        if self.value() == DUE_TO_EXPIRE or self._is_default(DUE_TO_EXPIRE):
            date_to = date_from + timedelta(days=DAYS)
            queryset = queryset.filter(
                expires__lte=date_to,
                expires__gt=date_from,
                #version__state="published",
            )
        elif self.value() == OVERDUE or self._is_default(OVERDUE):
            queryset = queryset.filter(
                expires__lte=date_from,
                #version__state="published",
            )
        return queryset

    def choices(self, changelist):
        for lookup, title in self.lookup_choices:
            lookup_value = str(lookup)
            yield {
                "selected": self.value() == lookup_value or self._is_default(lookup_value),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}
                ),
                "display": title,
            }