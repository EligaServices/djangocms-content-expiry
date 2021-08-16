HELPER_SETTINGS = {
    "TIME_ZONE": "America/Chicago",
    "INSTALLED_APPS": [
        "djangocms_content_expiry",
        "djangocms_content_expiry.test_utils.polls",
        "djangocms_versioning",
    ],
    "MIGRATION_MODULES": {
        "auth": None,
        "cms": None,
        "menus": None,
        "djangocms_versioning": None,
        "djangocms_content_expiry": None,
    },
    "CMS_PERMISSION": True,
    "LANGUAGES": (
        ("en", "English"),
        ("de", "German"),
        ("fr", "French"),
        ("it", "Italiano"),
    ),
    "CMS_LANGUAGES": {
        1: [
            {"code": "en", "name": "English", "fallbacks": ["de", "fr"]},
            {
                "code": "de",
                "name": "Deutsche",
                "fallbacks": ["en"],  # FOR TESTING DO NOT ADD 'fr' HERE
            },
            {
                "code": "fr",
                "name": "Française",
                "fallbacks": ["en"],  # FOR TESTING DO NOT ADD 'de' HERE
            },
            {
                "code": "it",
                "name": "Italiano",
                "fallbacks": ["fr"],  # FOR TESTING, LEAVE AS ONLY 'fr'
            },
        ]
    },
    "PARLER_ENABLE_CACHING": False,
    "LANGUAGE_CODE": "en",
}


def run():
    from app_helper import runner

    runner.cms("djangocms_content_expiry")


if __name__ == "__main__":
    run()
