"""MobileFarm OTA server module."""

import logging
from argparse import Namespace

from boardfarm3 import hookimpl
from boardfarm3.devices.base_devices import LinuxDevice
from boardfarm3.lib.boardfarm_pexpect import BoardfarmPexpect

from mobilefarm.templates.ota_server import OTAServerTemplate

_LOGGER = logging.getLogger(__name__)


class OTAServer(LinuxDevice, OTAServerTemplate):
    """MobileFarm OTA server device."""

    def __init__(self, config: dict, cmdline_args: Namespace) -> None:
        """Initialize MobileFarm OTA server device.

        :param config: OTA server device configuration
        :type config: dict
        :param cmdline_args: command line arguments
        :type cmdline_args: Namespace
        """
        super().__init__(config, cmdline_args)

    @hookimpl
    def boardfarm_server_boot(self) -> None:
        """Boardfarm hook implementation to boot LAN device."""
        _LOGGER.info("Booting %s(%s) device", self.device_name, self.device_type)
        self._connect()

    @property
    def console(self) -> BoardfarmPexpect:
        """Returns OTA server console.

        :return: console
        :rtype: BoardfarmPexpect
        """
        return self._console

    def get_interactive_consoles(self) -> dict[str, BoardfarmPexpect]:
        """Get interactive consoles from device.

        :return: interactive consoles of the device
        :rtype: dict[str, BoardfarmPexpect]
        """
        return {"ota_server": self._console}

    def fetch_ota_package(
        self, target: str, build_id: str, artifact_name: str, output: str
    ) -> None:
        """Fetch OTA package from using `fetch_artifact` CLI command.

        :param target: Target device
        :type target: str
        :param build_id: Build ID of the OTA package to fetch
        :type build_id: str
        :param artifact_name: Name of the OTA artifact to fetch
        :type artifact_name: str
        :param output: Output file name for the fetched OTA package
        :type output: str
        :raises NotImplementedError: if not implemented
        """
        fetch_command = f"fetch_artifact --target {target} --build-id {build_id} --artifact-name {artifact_name} --output {output}"
        self._console.execute_command(fetch_command)

    @hookimpl
    def boardfarm_skip_boot(self) -> None:
        """Boot Google Pixel 8 Pro with skip-boot option."""
        _LOGGER.info(
            "Initializing %s(%s) device with skip-boot option",
            self.device_name,
            self.device_type,
        )
        self._connect()
