"""Mobilefarm GUI library."""

from __future__ import annotations

import logging
import pathlib
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from appium import webdriver
from appium.options.android.uiautomator2.base import UiAutomator2Options
from boardfarm3.lib.utils import get_pytest_name
from selenium.webdriver.support.abstract_event_listener import AbstractEventListener
from selenium.webdriver.support.event_firing_webdriver import EventFiringWebDriver
from selenium.webdriver.support.wait import WebDriverWait

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver
    from selenium.webdriver.remote.webelement import WebElement

_LOGGER = logging.getLogger(__name__)


def get_web_driver(default_delay: int) -> WebDriver:
    """Return Appium webdriver.

    :param default_delay: default delay in seconds
    :type default_delay: int
    :return: configured Appium webdriver instance
    :rtype: WebDriver
    """
    return appium_webproxy_driver(
        default_delay=default_delay,
    )


def appium_webproxy_driver(
    default_delay: int,
) -> WebDriver:
    """Initialize Appium webdriver.

    :param default_delay: selenium default delay in seconds
    :type default_delay: int
    :param headless: headless state, default to False
    :type headless: bool
    :return: gui selenium web driver instance
    :rtype: WebDriver
    """
    caps = {
        "platformName": "Android",
        "automationName": "UiAutomator2",
        "deviceName": "Android",
        "appPackage": "com.android.settings",
        "appActivity": ".Settings",
        "noReset": True,
        "language": "en",
        "locale": "US",
    }

    driver = webdriver.Remote(
        "http://localhost:4723",
        options=UiAutomator2Options().load_capabilities(caps),
    )
    driver.implicitly_wait(default_delay)
    return driver


class AndroidScreenshotListener(AbstractEventListener):
    """Take a screenshot on exceptions/events.

    This allows to capture screenshot based on selenium web driver events.
    Capturing screenshot can be varied by setting the logging.root.level
    When logging.root.level set to :

        1. NOTSET - takes screenshots for on_exception and before_click events
        2. INFO   - takes screenshots for on_exception, before_click and
                            after_change_value_of events
        3. DEBUG  - takes screenshot for all the events
    """

    debug_enabled = logging.root.level in (logging.DEBUG, logging.INFO)
    verbose_debug_enabled = logging.root.level == logging.DEBUG

    def __init__(self, screenshot_path: str) -> None:
        """Init method.

        :param screenshot_path: the screenshot destination dir
        :type screenshot_path: str
        """
        super().__init__()
        self.screenshot_dir = Path(screenshot_path)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    def capture_screenshot(
        self, driver: WebDriver, name: str, ext: str = "png"
    ) -> None:
        """Capture screenshot and save name.ext to disk.

        :param driver: web driver
        :type driver: WebDriver
        :param name: the filename (with path if needed)
        :type name: str
        :param ext: the extension, defaults to png
        :type ext: str
        """
        now = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S%f")
        file_path = self.screenshot_dir / f"{now}_{name}.{ext}"

        WebDriverWait(driver, 3).until(lambda d: d.page_source)

        try:
            driver.get_screenshot_as_file(str(file_path))
            _LOGGER.debug("Screenshot saved: %s", file_path)
        except Exception as exc:
            _LOGGER.warning("Failed to capture screenshot: %s", exc)

    def on_exception(
        self,
        exception: Exception,  # noqa: ARG002
        driver: WebDriver,
    ) -> None:
        """Capture screenshot on exception.

        :param exception: unused
        :type exception: Exception
        :param driver: web driver
        :type driver: WebDriver
        """
        self.capture_screenshot(driver, "Exception")

    def before_navigate_to(
        self,
        url: str,  # noqa: ARG002
        driver: WebDriver,
    ) -> None:
        """Capture screenshot before navigate_to event.

        :param url: unused
        :type url: str
        :param driver: web driver
        :type driver: WebDriver
        """
        if self.verbose_debug_enabled:
            self.capture_screenshot(driver, "before_navigate_to")

    def after_navigate_to(
        self,
        url: str,  # noqa: ARG002
        driver: WebDriver,
    ) -> None:
        """Capture screenshot after navigate_to event.

        :param url: unused
        :type url: str
        :param driver: web driver
        :type driver: WebDriver
        """
        if self.verbose_debug_enabled:
            self.capture_screenshot(driver, "after_navigate_to")

    def before_click(
        self,
        element: WebElement,  # noqa: ARG002
        driver: WebDriver,
    ) -> None:
        """Capture screenshot before click event.

        :param element: unused
        :type element: WebElement
        :param driver: web driver
        :type driver: WebDriver
        """
        self.capture_screenshot(driver, "before_click")

    def after_click(
        self,
        element: WebElement,  # noqa: ARG002
        driver: WebDriver,
    ) -> None:
        """Capture screenshot after click event.

        :param element: unused
        :type element: WebElement
        :param driver: web driver
        :type driver: WebDriver
        """
        if self.verbose_debug_enabled:
            self.capture_screenshot(driver, "after_click")

    def before_change_value_of(
        self,
        element: WebElement,  # noqa: ARG002
        driver: WebDriver,
    ) -> None:
        """Capture screenshot before change_value_of event.

        :param element: unused
        :type element: WebElement
        :param driver: web driver
        :type driver: WebDriver
        """
        if self.verbose_debug_enabled:
            self.capture_screenshot(driver, "before_change_value_of")

    def after_change_value_of(
        self,
        element: WebElement,  # noqa: ARG002
        driver: WebDriver,
    ) -> None:
        """Capture screenshot after change_value_of event.

        :param element: unused
        :type element: WebElement
        :param driver: web driver
        :type driver: WebDriver
        """
        if self.verbose_debug_enabled or self.debug_enabled:
            self.capture_screenshot(driver, "after_change_value_of")

    def before_execute_script(
        self,
        script: str,  # noqa: ARG002
        driver: WebDriver,
    ) -> None:
        """Capture screenshot before execute_script event.

        :param script: unused
        :type script: str
        :param driver: web driver
        :type driver: WebDriver
        """
        if self.verbose_debug_enabled:
            self.capture_screenshot(driver, "before_execute_script")

    def after_execute_script(
        self,
        script: str,  # noqa: ARG002
        driver: WebDriver,
    ) -> None:
        """Capture screenshot after execute_script event.

        :param script: unused
        :type script: str
        :param driver: web driver
        :type driver: WebDriver
        """
        if self.verbose_debug_enabled:
            self.capture_screenshot(driver, "after_execute_script")

    def before_close(self, driver: WebDriver) -> None:
        """Capture screenshot before close event.

        :param driver: web driver
        :type driver: WebDriver
        """
        if self.verbose_debug_enabled:
            self.capture_screenshot(driver, "before_close")

    def after_close(self, driver: WebDriver) -> None:
        """Capture screenshot after close event.

        :param driver: web driver
        :type driver: WebDriver
        """
        if self.verbose_debug_enabled:
            self.capture_screenshot(driver, "after_close")

    def before_quit(self, driver: WebDriver) -> None:
        """Capture screenshot before quit event.

        :param driver: web driver
        :type driver: WebDriver
        """
        if self.verbose_debug_enabled:
            self.capture_screenshot(driver, "before_quit")


class AndroidGuiHelper:
    """GuiHelper class to get webdrivers for testing."""

    _headless: bool = True

    def __init__(
        self,
        default_delay: int = 20,
        output_dir: str | None = None,
    ) -> None:
        """GUI helper class.

        :param default_delay: default delay in seconds, defaults to 20
        :type default_delay: int
        :param output_dir: output directory path, defaults to None
        :type output_dir: str | None
        """
        if output_dir is None:
            output_dir = pathlib.Path.cwd().joinpath("results").as_posix()
        self._default_delay = default_delay
        self._test_name = get_pytest_name()
        self._screenshot_path = str(
            (pathlib.Path(output_dir).resolve()).joinpath(self._test_name)
        )

    def get_web_driver(self) -> EventFiringWebDriver:
        """Return event firing web driver.

        :return: web driver instance
        :rtype: EventFiringWebDriver
        """
        web_driver = get_web_driver(self._default_delay)
        event_firing_webdriver = EventFiringWebDriver(
            web_driver, AndroidScreenshotListener(self._screenshot_path)
        )
        event_firing_webdriver.screenshot_path = self._screenshot_path
        return event_firing_webdriver

    def get_webdriver_without_event_firing(self) -> WebDriver:
        """Return webdriver without the EventFiringWebDriver.

        :return: web driver instance
        :rtype: WebDriver
        """
        driver = get_web_driver(self._default_delay)
        driver.screenshot_path = self._screenshot_path  # type: ignore[attr-defined]
        return driver
