"""MobileFarm OTA server module."""

import ast
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
        """Boardfarm hook implementation to boot OTA server."""
        _LOGGER.info("Booting %s(%s) device", self.device_name, self.device_type)
        self._connect()

    @hookimpl
    def boardfarm_shutdown_device(self) -> None:
        """Boardfarm hook implementation to shutdown OTA server."""
        _LOGGER.info("Shutdown %s(%s) device", self.device_name, self.device_type)
        self._disconnect()

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
        fetch_command = f"fetch_artifact -target {target} -build_id {build_id} -artifact {artifact_name} -output {output}"
        self._console.execute_command(fetch_command, timeout=60)

    @hookimpl
    def boardfarm_skip_boot(self) -> None:
        """Boot OTA server with skip-boot option."""
        _LOGGER.info(
            "Initializing %s(%s) device with skip-boot option",
            self.device_name,
            self.device_type,
        )
        self._connect()

    def _parse_ota_metadata(
        self, artifact_name: str, secondary: bool
    ) -> tuple[int, int, list[str]]:
        secondary_flag = "--secondary" if secondary else ""
        output = self._console.execute_command(
            f"python3 /usr/local/bin/parse_ota_metadata.py "
            f"{artifact_name} {secondary_flag}",
            timeout=30,
        )
        offset, size, headers_raw = output.split(",", 2)
        headers_raw = ast.literal_eval(headers_raw.strip())
        headers_raw += b"USER_AGENT=Dalvik (something, something)\n"
        headers_raw += b"NETWORK_ID=0\n"
        return int(offset.strip()), int(size.strip()), headers_raw.decode("utf-8")

    def serve_ota_package(
        self,
        target: str,
        build_id: str,
        artifact_name: str,
        secondary_payload: bool = False,
    ) -> tuple[str, int, int, bytes]:
        """Fetch OTA package and place it in /tftpboot for serving.

        :param target: Target device
        :type target: str
        :param build_id: Build ID of the OTA package to fetch
        :type build_id: str
        :param artifact_name: Name of the OTA artifact to fetch
        :type artifact_name: str
        :param secondary_payload: Use secondary payload entries if True
        :type secondary_payload: bool
        :return: URL of the served OTA package, payload offset, payload size,
            payload properties
        :rtype: tuple[str, int, int, bytes]
        """
        self.fetch_ota_package(
            target=target,
            build_id=build_id,
            artifact_name=artifact_name,
            output=artifact_name,
        )
        self._console.execute_command(f"mv {artifact_name} /tftpboot/")
        self._console.execute_command(f"chmod 644 /tftpboot/{artifact_name}")

        ota_zip_path = f"/tftpboot/{artifact_name}"
        offset, size, properties = self._parse_ota_metadata(
            ota_zip_path, secondary_payload
        )

        server_ip = self._config["ipaddr"]
        port = self._config.get("ota_http_port", 80)
        url = f"http://{server_ip}:{port}/{artifact_name}"
        return url, offset, size, properties
