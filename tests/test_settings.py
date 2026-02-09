"""Get the current software version test for Pixel 8 Pro device."""

import pytest
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from pytest_boardfarm3.lib.test_logger import TestLogger


@pytest.mark.env_req({"environment_def": {"pixel8_pro": {}}})
def test_get_current_software_version(
    bf_logger: TestLogger,
    browser_data_visual_regression: WebDriver,
) -> None:
    """Test to get the current software version of the device.

    :param bf_logger: Test logger instance for logging test steps and results
    :type bf_logger: TestLogger
    :param browser_data_visual_regression: Appium WebDriver instance for visual
        regression testing
    :type browser_data_visual_regression: WebDriver
    """
    driver = browser_data_visual_regression

    bf_logger.log_step("Open Settings app")
    driver.activate_app("com.android.settings")

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
