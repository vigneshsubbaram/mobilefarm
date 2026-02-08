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
    build_number_el = driver.find_element(
        AppiumBy.ANDROID_UIAUTOMATOR,
        "new UiScrollable(new UiSelector().scrollable(true))"
        '.scrollIntoView(new UiSelector().text("Build number"))',
    )

    build_number = build_number_el.text
    bf_logger.log_step(f"Build number: {build_number}")

    assert build_number, "Build number should not be empty"
