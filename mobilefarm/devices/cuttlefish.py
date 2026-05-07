"""MobileFarm Cuttlefish device module."""

import logging
import re
import shlex
import time
from argparse import Namespace

import pexpect
from boardfarm3 import hookimpl
from boardfarm3.devices.base_devices import LinuxDevice
from boardfarm3.exceptions import DeviceConnectionError
from boardfarm3.lib.boardfarm_pexpect import BoardfarmPexpect
from boardfarm3.lib.connection_factory import connection_factory
from boardfarm3.lib.device_manager import DeviceManager

from mobilefarm.templates.android import AndroidTemplate
from mobilefarm.templates.ota_server import OTAServerTemplate

_LOGGER = logging.getLogger(__name__)


class CuttleFish(LinuxDevice, AndroidTemplate):
    """MobileFarm Cuttlefish device."""

    def __init__(self, config: dict, cmdline_args: Namespace) -> None:
        """Initialize mobilefarm Cuttlefish device.

        :param config: device configuration
        :type config: dict
        :param cmdline_args: command line arguments
        :type cmdline_args: Namespace
        """
        super().__init__(config, cmdline_args)
        self._config = config
        self._console: BoardfarmPexpect
        self._shell_prompt = [r".*\/ \$"]
        self._ota_url: str

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

    @property
    def build_id(self) -> str:
        """Returns the build ID of the Cuttlefish image.

        :return: build ID
        :rtype: str
        """
        return self._config["software"]["build_id"]

    @property
    def target(self) -> str:
        """Returns the target device configuration.

        :return: target device
        :rtype: str
        """
        return self._config["software"]["target"]

    @property
    def adb_target(self) -> str:
        """Returns the ADB target for the device.

        :return: ADB target
        :rtype: str
        """
        parts = shlex.split(self._config["conn_cmd"])
        return parts[2].split()[2]

    @property
    def artifact_name(self) -> str:
        """Returns the OTA artifact name to fetch from the OTA server.

        :return: OTA artifact name
        :rtype: str
        """
        return f"{self.target.split('-')[0]}-ota-{self.build_id}.zip"

    def get_interactive_consoles(self) -> dict[str, BoardfarmPexpect]:
        """Get interactive consoles from device.

        :return: interactive consoles of the device
        :rtype: dict[str, BoardfarmPexpect]
        """
        return {"cuttlefish": self._console}

    @hookimpl
    def boardfarm_skip_boot(self) -> None:
        """Boot Cuttlefish with skip-boot option."""
        _LOGGER.info(
            "Initializing %s(%s) device with skip-boot option",
            self.device_name,
            self.device_type,
        )
        self._connect_to_console()

    @hookimpl
    def boardfarm_shutdown_device(self) -> None:
        """Boardfarm hook implementation to shutdown Cuttlefish."""
        _LOGGER.info("Shutdown %s(%s) device", self.device_name, self.device_type)
        self._disconnect()

    @hookimpl
    def boardfarm_device_boot(self, device_manager: DeviceManager) -> None:
        """Boot cuttlefish device and trigger OTA update if configured.

        :param device_manager: device manager instance
        :type device_manager: DeviceManager
        """
        _LOGGER.info(
            "Booting %s(%s) device",
            self.device_name,
            self.device_type,
        )
        ota_server = device_manager.get_device_by_type(
            OTAServerTemplate,  # type:ignore[type-abstract]
        )
        self._connect_to_console()
        self._ota_url, self._ota_offset, self._ota_size, self._ota_properties = (
            ota_server.serve_ota_package(
                target=self.target,
                build_id=self.build_id,
                artifact_name=self.artifact_name,
                secondary_payload=self._config.get("secondary_payload", False),
            )
        )
        self._trigger_ota_update()
        self._wait_for_reboot()

    def _trigger_ota_update(self) -> None:
        """Trigger A/B OTA update using update_engine_client.

        Parses the OTA zip locally to extract payload offset, size and
        payload_properties headers. The device fetches the zip directly
        from the OTA server over HTTP using the --http-url pattern from
        the AOSP ota_from_target_files script.
        """
        self._console.execute_command("stty cols 10000")
        update_cmd = (
            f"su 0 update_engine_client --update --follow "
            f"--payload={self._ota_url} "
            f"--offset={self._ota_offset} "
            f"--size={self._ota_size} "
            f"--headers='{self._ota_properties}'"
        )
        _LOGGER.info(
            "Triggering OTA on %s: url=%s offset=%d size=%d",
            self.device_name,
            self._ota_url,
            self._ota_offset,
            self._ota_size,
        )
        success_pattern = re.escape(
            "onPayloadApplicationComplete(ErrorCode::kSuccess (0))"
        )
        self._console.sendline(update_cmd)
        self._console.expect(success_pattern, timeout=1800)

    def _wait_for_reboot(self) -> None:
        """Reboot into the updated slot and wait for the shell prompt."""
        _LOGGER.info("Rebooting %s into updated slot", self.device_name)
        self._console.sendline("svc power reboot")
        self._console.expect([pexpect.EOF, pexpect.TIMEOUT], timeout=10)
        self._console.close()
        self._wait_for_adb_online(timeout=600)
        self._connect_to_console()
        _LOGGER.info("Device back online after OTA, build_id=%s", self.build_id)

    def _wait_for_adb_online(self, timeout: int = 300) -> None:
        """Wait for the device to be online over ADB.

        :param timeout: maximum time to wait for the device to be online, in seconds
        :type timeout: int
        """
        _LOGGER.info("Waiting for %s to be online over ADB", self.device_name)

        deadline = time.monotonic() + timeout
        poll_interval = 5

        while time.monotonic() < deadline:
            parts = shlex.split(self._config["conn_cmd"])
            try:
                probe = connection_factory(
                    connection_type=str(self._config.get("connection_type")),
                    connection_name=f"{self.device_name}.console",
                    conn_command=parts[0],
                    args=parts[1:],
                    save_console_logs=self._cmdline_args.save_console_logs,
                    shell_prompt=self._shell_prompt,
                )
                probe.login_to_server()
                probe.sendline("uptime")
                index = probe.expect(self._shell_prompt, timeout=5)
                if index == 0:
                    _LOGGER.info("%s is online over ADB", self.device_name)
                    probe.close()
                    return
            except DeviceConnectionError as e:
                _LOGGER.warning(
                    "Waiting for device %s to be online over ADB: %s",
                    self.device_name,
                    str(e),
                )
            finally:
                probe.close()
            time.sleep(poll_interval)
        err_msg = f"Timed out waiting for {self.device_name} to be online over ADB after {timeout} seconds"
        raise TimeoutError(err_msg)
