"""MobileFarm Google Pixel 8 Pro module."""

import logging
from argparse import Namespace

from boardfarm3 import hookimpl
from boardfarm3.devices.base_devices.boardfarm_device import BoardfarmDevice
from boardfarm3.lib.boardfarm_pexpect import BoardfarmPexpect
from boardfarm3.lib.connection_factory import connection_factory

from mobilefarm.templates.android import AndroidTemplate

_LOGGER = logging.getLogger(__name__)


class Pixel8Pro(BoardfarmDevice, AndroidTemplate):
    """MobileFarm Google Pixel 8 Pro device."""

    def __init__(self, config: dict, cmdline_args: Namespace) -> None:
        """Initialize mobilefarm Google Pixel 8 Pro.

        :param config: device configuration
        :type config: dict
        :param cmdline_args: command line arguments
        :type cmdline_args: Namespace
        """
        super().__init__(config, cmdline_args)
        self._console: BoardfarmPexpect | None = None
        self._shell_prompt = [r".*\/ \$"]

    def _connect_to_console(self) -> None:
        self._console = connection_factory(
            connection_type=str(self._config.get("connection_type")),
            connection_name=f"{self.device_name}.console",
            conn_command=self._config["conn_cmd"][0],
            save_console_logs=self._cmdline_args.save_console_logs,
            shell_prompt=self._shell_prompt,
        )
        self._console.login_to_server()

    @hookimpl
    def boardfarm_server_boot(self) -> None:
        """Boot Google Pixel 8 Pro."""
        _LOGGER.info(
            "Booting %s(%s) device",
            self.device_name,
            self.device_type,
        )
        self._connect_to_console()

    @hookimpl
    def boardfarm_skip_boot(self) -> None:
        """Boot Google Pixel 8 Pro with skip-boot option."""
        _LOGGER.info(
            "Initializing %s(%s) device with skip-boot option",
            self.device_name,
            self.device_type,
        )
        self._connect_to_console()

    @hookimpl
    def boardfarm_device_boot_async(self) -> None:
        """Boot Google Pixel 8 Pro asynchronously."""
        err_msg = "Asynchronous boot not supported for Pixel 8 Pro"
        raise NotImplementedError(err_msg)

    @property
    def console(self) -> BoardfarmPexpect:
        """Returns Google Pixel 8 Pro console.

        :return: console
        :rtype: BoardfarmPexpect
        """
        return self._console

    def get_interactive_consoles(self) -> dict[str, BoardfarmPexpect]:
        """Get interactive consoles from device.

        :returns: interactive consoles of the device
        """
        return {"pixel8_pro": self._console}
