"""Test alarm functionality in Google Pixel 8 Pro device."""

from datetime import datetime, timedelta, timezone

import pytest
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webdriver import WebDriver
from pytest_boardfarm3.lib.test_logger import TestLogger
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

_HOURS_IN_12_HOUR_FORMAT = 12


@pytest.mark.env_req(
    {
        "environment_def": {
            "pixel8_pro": {
                "model": "pixel8_pro",
                "app_package": "com.google.android.deskclock",
                "app_activity": "com.android.deskclock.DeskClock",
            }
        }
    }
)
def test_set_alarm(
    bf_logger: TestLogger,
    android_web_driver: WebDriver,
) -> None:
    """Test to set an alarm on the device.

    :param bf_logger: Test logger instance for logging test steps and results
    :type bf_logger: TestLogger
    :param android_web_driver: Appium WebDriver instance for Android device testing
    :type android_web_driver: WebDriver
    """
    driver = android_web_driver
    bf_logger.log_step("Open Alarm app")

    alarm_tab = driver.find_element(AppiumBy.ID, "com.google.android.deskclock:id/fab")
    alarm_tab.click()

    future_time = datetime.now(timezone.utc) + timedelta(minutes=2)
    hour = future_time.hour
    minute = future_time.minute

    hour_12 = hour % _HOURS_IN_12_HOUR_FORMAT or _HOURS_IN_12_HOUR_FORMAT
    is_pm = hour >= _HOURS_IN_12_HOUR_FORMAT

    bf_logger.log_step(
        f"Set alarm time to {hour_12:02d}:{minute:02d} {'PM' if is_pm else 'AM'}"
    )

    # Select AM / PM explicitly
    driver.find_element(
        AppiumBy.ID,
        (
            "com.google.android.deskclock:id/material_clock_period_pm_button"
            if is_pm
            else "com.google.android.deskclock:id/material_clock_period_am_button"
        ),
    ).click()

    driver.find_element(
        AppiumBy.ACCESSIBILITY_ID,
        f"Hour {((hour % _HOURS_IN_12_HOUR_FORMAT) + 1) or _HOURS_IN_12_HOUR_FORMAT} o'clock",
    ).click()

    hour_input = driver.switch_to.active_element
    hour_input.clear()
    hour_input.send_keys(f"{hour_12:02d}")

    driver.find_element(
        AppiumBy.ACCESSIBILITY_ID,
        "Minute 0 minutes",
    ).click()

    minute_input = driver.switch_to.active_element
    minute_input.clear()
    minute_input.send_keys(f"{minute:02d}")

    driver.find_element(
        by=AppiumBy.ID,
        value="com.google.android.deskclock:id/material_timepicker_ok_button",
    ).click()

    driver.open_notifications()

    wait = WebDriverWait(driver, 120)

    try:
        wait.until(
            EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "Stop"))
        ).click()
    except TimeoutException:
        bf_logger.log_step("Alarm did not trigger within expected time frame")
        raise
