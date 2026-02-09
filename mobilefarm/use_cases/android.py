"""MobileFarm use cases for Android devices."""

from selenium.webdriver.support.event_firing_webdriver import EventFiringWebDriver

from mobilefarm.templates.android import AndroidTemplate


def open_application(device: AndroidTemplate, driver: EventFiringWebDriver) -> None:
    """Open an application present in the env on the device.

    :param device: Android device instance
    :type device: AndroidTemplate
    :param driver: Appium WebDriver instance for interacting with the device
    :type driver: EventFiringWebDriver
    """
    driver.activate_app(device.app_package)
