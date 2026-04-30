"""MobileFarm Cuttlefish device module."""

import logging
import shlex
from argparse import Namespace

from boardfarm3 import hookimpl
from boardfarm3.devices.base_devices import LinuxDevice
from boardfarm3.lib.boardfarm_pexpect import BoardfarmPexpect
from boardfarm3.lib.connection_factory import connection_factory

from mobilefarm.templates.android import AndroidTemplate

_LOGGER = logging.getLogger(__name__)


class CuttleFish(LinuxDevice, AndroidTemplate):
    """MobileFarm Google Pixel 8 Pro device."""

    def __init__(self, config: dict, cmdline_args: Namespace) -> None:
        """Initialize mobilefarm Google Pixel 8 Pro.

        :param config: device configuration
        :type config: dict
        :param cmdline_args: command line arguments
        :type cmdline_args: Namespace
        """
        super().__init__(config, cmdline_args)
        self._config = config
        self._console: BoardfarmPexpect | None = None
        self._shell_prompt = [r".*\/ \$"]

    def _connect_to_console(self) -> None:
        parts = shlex.split(self._config["conn_cmd"])
        _LOGGER.warning(self._config["conn_cmd"])
        self._console = connection_factory(
            connection_type=str(self._config.get("connection_type")),
            connection_name=f"{self.device_name}.console",
            conn_command=parts[0],
            args=parts[1:],
            save_console_logs=self._cmdline_args.save_console_logs,
            shell_prompt=self._shell_prompt,
        )
        self._console.login_to_server()

    @property
    def app_package(self) -> str:
        """Device app package."""
        return self._config.get("app_package", "com.android.settings")

    @property
    def app_activity(self) -> str:
        """Device app activity."""
        return self._config.get("app_activity", ".Settings")

    @property
    def console(self) -> BoardfarmPexpect:
        """Returns the Cuttlefish console.

        :return: console
        :rtype: BoardfarmPexpect
        """
        return self._console

    def get_interactive_consoles(self) -> dict[str, BoardfarmPexpect]:
        """Get interactive consoles from device.

        :return: interactive consoles of the device
        :rtype: dict[str, BoardfarmPexpect]
        """
        return {"cuttlefish": self._console}

    @hookimpl
    def boardfarm_skip_boot(self) -> None:
        """Boot Google Pixel 8 Pro with skip-boot option."""
        _LOGGER.info(
            "Initializing %s(%s) device with skip-boot option",
            self.device_name,
            self.device_type,
        )
        self._connect_to_console()
