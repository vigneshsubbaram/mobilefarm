"""Get the current software version test for Pixel 8 Pro device."""

import pytest
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from pytest_boardfarm3.lib.test_logger import TestLogger


@pytest.mark.env_req(
    {
        "environment_def": {
            "pixel8_pro": {
                "model": "pixel8_pro",
                "app_package": "com.android.settings",
                "app_activity": ".Settings",
            }
        }
    }
)
def test_get_current_software_version(
    bf_logger: TestLogger,
    android_web_driver: WebDriver,
) -> None:
    """Test to get the current software version of the device.

    :param bf_logger: Test logger instance for logging test steps and results
    :type bf_logger: TestLogger
    :param android_web_driver: Appium WebDriver instance for Android device testing
    :type android_web_driver: WebDriver
    """
    bf_logger.log_step("Open Settings app")
    driver = android_web_driver

    bf_logger.log_step("Open About phone")
    about_phone = driver.find_element(
        AppiumBy.ANDROID_UIAUTOMATOR,
        "new UiScrollable(new UiSelector().scrollable(true))"
        '.scrollIntoView(new UiSelector().text("About phone"))',
    )
    about_phone.click()

    bf_logger.log_step("Scroll to Build number")
    driver.find_element(
        AppiumBy.ANDROID_UIAUTOMATOR,
        "new UiScrollable(new UiSelector().scrollable(true))"
        '.scrollIntoView(new UiSelector().text("Build number"))',
    )

    build_number_value = driver.find_element(
        AppiumBy.XPATH,
        '//android.widget.TextView[@resource-id="android:id/title" and @text="Build number"]'
        '/following-sibling::android.widget.TextView[@resource-id="android:id/summary"]',
    )
    build_number = build_number_value.text
    bf_logger.log_step(f"Build number: {build_number}")

    assert build_number, "Build number should not be empty"
