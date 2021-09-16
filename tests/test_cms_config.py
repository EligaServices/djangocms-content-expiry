from django.apps import apps

from djangocms_content_expiry.cms_config import ContentExpiryAppConfig

from djangocms_moderation.cms_config import ModerationExtension

from cms.test_utils.testcases import CMSTestCase


class ModerationConfigDependancyTestCase(CMSTestCase):
    def test_moderation_config_admin_controls_exist(self):
        """
        Moderation controls are required for the content expiry records to be viewed,
        ensure that they exist, a failure here means that the implementation in moderation
        may have been changed
        """
        moderation_extension = ModerationExtension()

        self.assertTrue(hasattr(moderation_extension, "moderation_request_changelist_actions"))
        self.assertTrue(hasattr(moderation_extension, "moderation_request_changelist_fields"))
        self.assertTrue(
            hasattr(moderation_extension, "handle_moderation_request_changelist_actions")
            and callable(moderation_extension.handle_moderation_request_changelist_actions)
        )
        self.assertTrue(
            hasattr(moderation_extension, "handle_moderation_request_changelist_fields")
            and callable(moderation_extension.handle_moderation_request_changelist_fields)
        )

    def test_moderation_config_admin_controls_are_compiled_by_moderation(self):
        moderation = apps.get_app_config("djangocms_moderation")
        content_expiry_actions = ContentExpiryAppConfig.moderation_request_changelist_actions
        content_expiry_fields = ContentExpiryAppConfig.moderation_request_changelist_fields

        self.assertListEqual(
            moderation.cms_extension.moderation_request_changelist_actions,
            content_expiry_actions,
        )
        self.assertListEqual(
            moderation.cms_extension.moderation_request_changelist_fields,
            content_expiry_fields,
        )
