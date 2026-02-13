"""MobileFarm use cases for Android devices."""

from collections.abc import Generator
from contextlib import contextmanager

from mobilefarm.lib.gui import AppiumDriverProxy
from mobilefarm.templates.android import AndroidTemplate


@contextmanager
def open_application(
    device: AndroidTemplate, driver: AppiumDriverProxy
) -> Generator[None, None, None]:
    """Open an application and ensure it's terminated on exit.

    :param device: Android device instance
    :type device: AndroidTemplate
    :param driver: Appium WebDriver instance for interacting with the device
    :type driver: AppiumDriverProxy
    :yields: None
    """
    driver.activate_app(device.app_package)
    try:
        yield
    finally:
        driver.terminate_app(device.app_package)
