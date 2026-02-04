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
    """Get the current software version test for Pixel 8 Pro device.

    :param bf_logger: The boardfarm logger
    :type bf_logger: TestLogger
    :param browser_data_visual_regression: WebDriver instance
    :type browser_data_visual_regression: WebDriver
    """
    bf_logger.log_step("Connect to Android Device")
    driver = browser_data_visual_regression
    bf_logger.log_step("Get current software version")
    el = driver.find_element(by=AppiumBy.XPATH, value='//*[@text="Apps"]')
    el.click()
