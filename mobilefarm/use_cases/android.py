"""MobileFarm use cases for Android devices."""

from appium.webdriver.webdriver import WebDriver

from mobilefarm.templates.android import AndroidTemplate


def open_application(device: AndroidTemplate, driver: WebDriver) -> None:
    """Open an application present in the env on the device.

    :param device: Android device instance
    :type device: AndroidTemplate
    :param driver: Appium WebDriver instance for interacting with the device
    :type driver: WebDriver
    """
    driver.activate_app(device.app_package)
