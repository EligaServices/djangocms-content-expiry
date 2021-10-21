import factory
from djangocms_versioning.models import Version
from djangocms_versioning.signals import post_version_operation, pre_version_operation
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyText

from djangocms_content_expiry.models import ContentExpiry
from djangocms_content_expiry.test_utils.factories import (
    AbstractVersionFactory,
    UserFactory,
)

from .models import (
    ProjectContent,
    ProjectGrouper,
    ArtProjectContent,
    ResearchProjectContent,
)


# Project models
class ProjectGrouperFactory(DjangoModelFactory):
    name = FuzzyText(length=10)

    class Meta:
        model = ProjectGrouper


class ProjectContentFactory(DjangoModelFactory):
    grouper = factory.SubFactory(ProjectGrouperFactory)
    topic = FuzzyText(length=20)

    class Meta:
        model = ProjectContent


class ProjectContentVersionFactory(AbstractVersionFactory):
    content = factory.SubFactory(ProjectContentFactory)

    class Meta:
        model = Version
        exclude = []


class ProjectContentWithVersionFactory(ProjectContentFactory):
    @factory.post_generation
    def version(self, create, extracted, **kwargs):
        if not create:
            return
        ProjectContentVersionFactory(content=self, **kwargs)


@factory.django.mute_signals(pre_version_operation, post_version_operation)
class ProjectContentExpiryFactory(DjangoModelFactory):
    created_by = factory.SubFactory(UserFactory)
    # FIXME: The fields for content.versions[x]:
    #        `content_type` and `content_type_id` are populated but the GenericForeignKey
    #        `content` is not. Could be cache or polymorphic related!
    #version = factory.SubFactory(ArtProjectContentVersionFactory)
    version = None
    expires = factory.Faker('date_object')

    class Meta:
        model = ContentExpiry


# Art Project models
class ArtProjectContentFactory(DjangoModelFactory):
    grouper = factory.SubFactory(ProjectGrouperFactory)
    artist = FuzzyText(length=20)

    class Meta:
        model = ArtProjectContent


class ArtProjectContentVersionFactory(AbstractVersionFactory):
    content = factory.SubFactory(ArtProjectContentFactory)

    class Meta:
        model = Version


class ArtProjectContentWithVersionFactory(ArtProjectContentFactory):
    @factory.post_generation
    def version(self, create, extracted, **kwargs):
        # NOTE: Use this method as below to define version attributes:
        # PollContentWithVersionFactory(version__label='label1')
        if not create:
            # Simple build, do nothing.
            return
        ArtProjectContentVersionFactory(content=self, **kwargs)


@factory.django.mute_signals(pre_version_operation, post_version_operation)
class ArtProjectContentExpiryFactory(DjangoModelFactory):
    created_by = factory.SubFactory(UserFactory)
    # FIXME: The fields for content.versions[x]:
    #        `content_type` and `content_type_id` are populated but the GenericForeignKey
    #        `content` is not. Could be cache or polymorphic related!
    #version = factory.SubFactory(ArtProjectContentVersionFactory)
    version = None
    expires = factory.Faker('date_object')

    class Meta:
        model = ContentExpiry


# Research Project models
class ResearchProjectContentFactory(DjangoModelFactory):
    grouper = factory.SubFactory(ProjectGrouperFactory)
    supervisor = FuzzyText(length=20)

    class Meta:
        model = ResearchProjectContent


class ResearchProjectContentVersionFactory(AbstractVersionFactory):
    content = factory.SubFactory(ResearchProjectContentFactory)

    class Meta:
        model = Version


class ResearchProjectContentWithVersionFactory(ResearchProjectContentFactory):
    @factory.post_generation
    def version(self, create, extracted, **kwargs):
        # NOTE: Use this method as below to define version attributes:
        # PollContentWithVersionFactory(version__label='label1')
        if not create:
            # Simple build, do nothing.
            return
        ResearchProjectContentVersionFactory(content=self, **kwargs)


@factory.django.mute_signals(pre_version_operation, post_version_operation)
class ResearchProjectContentExpiryFactory(DjangoModelFactory):
    created_by = factory.SubFactory(UserFactory)
    version = factory.SubFactory(ResearchProjectContentVersionFactory)
    expires = factory.Faker('date_object')

    class Meta:
        model = ContentExpiry
