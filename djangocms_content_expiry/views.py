from django.contrib.admin.views.main import ChangeList


class ContentExpiryChangeList(ChangeList):
    def get_queryset(self, request, *args, **kwargs):
        queryset = super().get_queryset(request, *args, **kwargs)

        content_types = None
        if "content_type" in self.params:
            content_types = self.params

        if not content_types:
            return queryset

        # Ensure that we are matching types int vs int
        content_types = [int(ctype) for ctype in content_types.split(',')]
        excludes = []

        # Build an exclusion list, this is caused by django-polymorphic models
        # where the Version content_type maps to the higher order model
        for expiry_record in queryset:
            self._process_item_for_possible_exclusion(expiry_record, content_types, excludes)

        return queryset.exclude(pk__in=excludes)