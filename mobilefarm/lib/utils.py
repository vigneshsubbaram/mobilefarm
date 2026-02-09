"""Mobilefarm common utilities module."""

from typing import Any


def get_capabilities(config: dict[Any, Any]) -> dict[str, Any]:
    """Get capabilities from config.

    :param config: device configuration
    :type config: dict[Any, Any]
    :return: capabilities for the device
    :rtype: dict[str, str]
    """
    return {
        "platformName": "Android",
        "automationName": "UiAutomator2",
        "deviceName": "Android",
        "appPackage": config.get("app_package", "com.android.settings"),
        "appActivity": config.get("app_activity", ".Settings"),
        "noReset": True,
        "language": "en",
        "locale": "US",
    }
