from django.conf import settings

from cms.app_base import CMSAppConfig, CMSAppExtension


class ContentExpiryAppExtension(CMSAppExtension):
    def __init__(self):
        from .monkeypatch import admin as monkeypatch_admin

    def configure_app(self, cms_config):
        pass


class ContentExpiryAppConfig(CMSAppConfig):
    djangocms_content_expiry_enabled = getattr(
        settings, "DJANGOCMS_CONTENT_EXPIRY_ENABLED", True
    )
