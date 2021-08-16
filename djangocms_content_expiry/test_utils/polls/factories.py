import factory
from factory.fuzzy import FuzzyChoice, FuzzyInteger, FuzzyText

from djangocms_versioning.models import Version

from djangocms_content_expiry.test_utils.factories import AbstractVersionFactory

from .models import Poll, PollContent


class PollFactory(factory.django.DjangoModelFactory):
    name = FuzzyText(length=6)

    class Meta:
        model = Poll


class PollContentFactory(factory.django.DjangoModelFactory):
    poll = factory.SubFactory(PollFactory)
    language = FuzzyChoice(["en", "fr", "it"])
    text = FuzzyText(length=24)

    class Meta:
        model = PollContent


class PollVersionFactory(AbstractVersionFactory):
    content = factory.SubFactory(PollContentFactory)

    class Meta:
        model = Version


class PollContentWithVersionFactory(PollContentFactory):
    @factory.post_generation
    def version(self, create, extracted, **kwargs):
        # NOTE: Use this method as below to define version attributes:
        # PollContentWithVersionFactory(version__label='label1')
        if not create:
            # Simple build, do nothing.
            return
        PollVersionFactory(content=self, **kwargs)
