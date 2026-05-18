"""Mobilefarm ATS device module."""

import logging
from argparse import Namespace

from boardfarm3 import hookimpl
from boardfarm3.devices.base_devices import LinuxDevice
from boardfarm3.lib.boardfarm_pexpect import BoardfarmPexpect

from mobilefarm.templates.ats import ATSTemplate

_LOGGER = logging.getLogger(__name__)


class AndroidTestStation(LinuxDevice, ATSTemplate):
    """Android Test Station device."""

    def __init__(self, config: dict, cmdline_args: Namespace) -> None:
        """Initialize Android Test Station device.

        :param config: Android Test Station device configuration
        :type config: dict
        :param cmdline_args: command line arguments
        :type cmdline_args: Namespace
        """
        super().__init__(config, cmdline_args)

    @hookimpl
    def boardfarm_server_boot(self) -> None:
        """Boardfarm hook implementation to boot Android Test Station."""
        _LOGGER.info("Booting %s(%s) device", self.device_name, self.device_type)
        self._connect()

    @hookimpl
    def boardfarm_shutdown_device(self) -> None:
        """Boardfarm hook implementation to shutdown Android Test Station."""
        _LOGGER.info("Shutdown %s(%s) device", self.device_name, self.device_type)
        self._disconnect()

    @property
    def console(self) -> BoardfarmPexpect:
        """Returns Android Test Station console.

        :return: console
        :rtype: BoardfarmPexpect
        """
        return self._console

    def get_interactive_consoles(self) -> dict[str, BoardfarmPexpect]:
        """Get interactive consoles from device.

        :return: interactive consoles of the device
        :rtype: dict[str, BoardfarmPexpect]
        """
        return {"android_test_station": self._console}

    @hookimpl
    def boardfarm_skip_boot(self) -> None:
        """Boot Android Test Station with skip-boot option."""
        _LOGGER.info(
            "Initializing %s(%s) device with skip-boot option",
            self.device_name,
            self.device_type,
        )
        self._connect()
