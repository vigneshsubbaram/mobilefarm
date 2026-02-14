"""Mobilefarm GUI library."""

from __future__ import annotations

import contextlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from appium import webdriver
from appium.options.android.uiautomator2.base import UiAutomator2Options
from boardfarm3.lib.utils import get_pytest_name
from selenium.webdriver.support.wait import WebDriverWait

from mobilefarm.lib.utils import get_capabilities

if TYPE_CHECKING:
    from appium.webdriver.webdriver import WebDriver
    from selenium.webdriver.remote.webelement import WebElement

_LOGGER = logging.getLogger(__name__)


class ScreenshotMixin:  # pylint: disable=too-few-public-methods
    """Mixin providing screenshot capture functionality."""

    screenshot_path: str
    _driver: WebDriver

    def _wait_for_ui_update(self, timeout: int = 2) -> None:
        """Wait for the UI hierarchy to stabilize."""
        with contextlib.suppress(Exception):
            WebDriverWait(self._driver, timeout).until(
                lambda d: (
                    d.page_source is not None
                    and d.current_package == self._driver.current_package
                )
            )

        with contextlib.suppress(Exception):
            self._driver.execute_script("mobile: waitForIdleSync", {"timeout": 5000})

    def capture_screenshot(self, name: str) -> None:
        """Capture a screenshot with a timestamped filename."""
        self._wait_for_ui_update()

        timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S%f")
        file_path = Path(self.screenshot_path) / f"{timestamp}_{name}.png"

        try:
            self._driver.get_screenshot_as_file(str(file_path))
            _LOGGER.debug("Screenshot saved: %s", file_path)
        except OSError as exc:
            _LOGGER.warning("Failed to capture screenshot: %s", exc)


class AppiumElementProxy(ScreenshotMixin):
    """Proxy around Appium WebElement to intercept actions."""

    def __init__(
        self, element: WebElement, driver: WebDriver, screenshot_path: str
    ) -> None:
        """Initialize element proxy.

        :param element: Original Appium WebElement
        :type element: WebElement
        :param driver: Appium WebDriver instance
        :type driver: WebDriver
        :param screenshot_path: Directory to store screenshots
        :type screenshot_path: str
        """
        self._element = element
        self._driver = driver
        self.screenshot_path = screenshot_path

    def click(self) -> None:
        """Click the element with before/after screenshots."""
        self.capture_screenshot("before_click")
        self._element.click()
        self.capture_screenshot("after_click")

    def send_keys(self, value: str) -> None:
        """Send keys to the element with screenshots.

        :param value: Text to send
        :type value: str
        """
        self.capture_screenshot("before_send_keys")
        self._element.send_keys(value)
        self.capture_screenshot("after_send_keys")

    def clear(self) -> None:
        """Clear element value with screenshots."""
        self.capture_screenshot("before_clear")
        self._element.clear()
        self.capture_screenshot("after_clear")

    def __getattr__(self, name: str) -> Any:  # noqa: ANN401
        """Delegate attribute access to the underlying element.

        :param name: Attribute name
        :type name: str
        :return: Attribute value from the original element
        :rtype: Any
        """
        return getattr(self._element, name)


class AppiumDriverProxy(ScreenshotMixin):
    """Proxy around Appium WebDriver to intercept driver-level actions."""

    def __init__(self, driver: WebDriver, screenshot_path: str) -> None:
        """Initialize driver proxy.

        :param driver: Appium WebDriver
        :type driver: WebDriver
        :param screenshot_path: Directory to store screenshots
        :type screenshot_path: str
        """
        self._driver = driver
        self.screenshot_path = screenshot_path

    def find_element(
        self, by: str, value: str | dict | None = None
    ) -> AppiumElementProxy:
        """Find an element and return a proxy that captures screenshots on interactions.

        :param by: Locator strategy (e.g., "id", "xpath")
        :type by: str
        :param value: Element locator value
        :type value: str | dict | None, optional
        :return: Wrapped Appium element proxy
        :rtype: AppiumElementProxy
        """
        element = self._driver.find_element(by, value)
        return AppiumElementProxy(element, self._driver, self.screenshot_path)

    def execute_script(self, script: str, *args: Any) -> Any:  # noqa: ANN401
        """Execute a script with screenshots.

        This captures *all* modern Appium gestures:
        swipe, scroll, drag, fling, etc.

        :param script: Script name
        :type script: str
        :return: Script result
        :rtype: Any
        """
        self.capture_screenshot("before_execute_script")
        result = self._driver.execute_script(script, *args)
        self.capture_screenshot("after_execute_script")
        return result

    def tap(
        self, positions: list[tuple[int, int]], duration: int | None = None
    ) -> None:
        """Tap on the screen with screenshots.

        :param positions: List of (x, y) coordinates to tap
        :type positions: list[tuple[int, int]]
        :param duration: Duration of the tap in ms (optional)
        :type duration: int | None
        """
        self.capture_screenshot("before_tap")
        self._driver.tap(positions, duration)
        self.capture_screenshot("after_tap")

    def swipe(  # noqa: PLR0913, RUF100
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: int,
    ) -> None:
        """Swipe with screenshots.

        :param start_x: Starting X coordinate
        :param start_y: Starting Y coordinate
        :param end_x: Ending X coordinate
        :param end_y: Ending Y coordinate
        :param duration: Swipe duration in ms
        """
        self.capture_screenshot("before_swipe")
        self._driver.swipe(start_x, start_y, end_x, end_y, duration)
        self.capture_screenshot("after_swipe")

    def activate_app(self, app_id: str) -> None:
        """Activate app with screenshots.

        :param app_id: Application package name
        :type app_id: str
        """
        self.capture_screenshot("before_activate_app")
        self._driver.activate_app(app_id)
        self.capture_screenshot("after_activate_app")

    def terminate_app(self, app_id: str) -> None:
        """Terminate app with screenshots.

        :param app_id: Application package name
        :type app_id: str
        """
        self.capture_screenshot("before_terminate_app")
        self._driver.terminate_app(app_id)
        self.capture_screenshot("after_terminate_app")

    def quit(self) -> None:  # noqa: A003, RUF100
        """Quit driver with final screenshot."""
        self.capture_screenshot("before_quit")
        self._driver.quit()

    def __getattr__(self, name: str) -> object:
        """Delegate attribute access to the underlying driver."""
        return getattr(self._driver, name)


class AndroidGuiHelper:  # pylint: disable=too-few-public-methods
    """GUI helper class to create Appium drivers with screenshot interception."""

    def __init__(
        self,
        config: dict[str, Any],
        default_delay: int = 20,
        output_dir: str | None = None,
    ) -> None:
        """Initialize GUI helper.

        :param config: Appium capabilities config
        :type config: dict[str, Any]
        :param default_delay: Implicit wait delay
        :type default_delay: int
        :param output_dir: Output directory for screenshots
        :type output_dir: str | None
        """
        if output_dir is None:
            output_dir = Path.cwd().joinpath("results").as_posix()

        self._default_delay = default_delay
        self._test_name = get_pytest_name()
        self._screenshot_path = str(
            Path(output_dir).resolve().joinpath(self._test_name)
        )
        Path(self._screenshot_path).mkdir(parents=True, exist_ok=True)
        self._capabilities = get_capabilities(config)
        self._disable_log_messages_from_libraries()

    def get_web_driver(self) -> AppiumDriverProxy:
        """Return wrapped Appium WebDriver.

        :return: Screenshot-enabled Appium driver
        :rtype: AppiumDriverProxy
        """
        raw_driver = webdriver.Remote(
            "http://localhost:4723",
            options=UiAutomator2Options().load_capabilities(self._capabilities),
        )
        raw_driver.implicitly_wait(self._default_delay)

        return AppiumDriverProxy(raw_driver, self._screenshot_path)

    def _disable_log_messages_from_libraries(self) -> None:
        """Disable logs from urllib3."""
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("selenium").setLevel(logging.WARNING)
