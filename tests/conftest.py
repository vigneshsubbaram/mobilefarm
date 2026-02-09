"""Pytest contest module."""

import logging
from collections.abc import Generator

import pytest
from _pytest.fixtures import FixtureRequest
from boardfarm3.lib.device_manager import get_device_manager

from mobilefarm.lib.gui import AndroidGuiHelper
from mobilefarm.templates.android import AndroidTemplate

_LOGGER = logging.getLogger(__name__)


class TestDetails:  # pylint: disable=too-few-public-methods
    """TestDetails helper class."""

    def __init__(self) -> None:
        """Test details helper class."""
        self.test_name = ""
        self.saved = False


@pytest.fixture(scope="session")
def get_output_dir(request: FixtureRequest) -> str:
    """Fixture to get the output dir from cmd line.

    :param request: a pytest helper fixture
    :type request: FixtureRequest
    :return: the results directory
    :rtype: str
    """
    return request.config.getoption("--save-console-logs")


@pytest.fixture()
def get_test_data() -> TestDetails:
    """Fixture for getting all test data.

    :return: the test details
    :rtype: TestDetails
    """
    return TestDetails()


@pytest.fixture()
def browser_data_visual_regression(
    get_test_data: TestDetails,  # pylint: disable=redefined-outer-name
) -> Generator:
    """Fixture for the VisReg.

    :param get_output_dir: the results directory path
    :type get_output_dir: str
    :param get_test_data: test context holder
    :type get_test_data: TestDetails
    :raises RuntimeError: _if a screenshot is saved (i.e. in the very first run)
    :yield: the driver
    :rtype: Generator
    """
    logging.basicConfig(level=logging.DEBUG)
    android_device = get_device_manager().get_device_by_type(
        device_type=AndroidTemplate  # type:ignore[type-abstract]
    )
    driver = AndroidGuiHelper(android_device.config).get_web_driver()

    yield driver

    driver.terminate_app("com.android.settings")
    driver.quit()
    test_details = get_test_data
    if test_details.saved:
        msg = "This test saved an attachment."
        _LOGGER.critical(msg)
        raise RuntimeError(msg)
