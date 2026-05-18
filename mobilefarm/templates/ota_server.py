"""MobileFarm OTA server template."""

from abc import ABC, abstractmethod

from boardfarm3.lib.boardfarm_pexpect import BoardfarmPexpect


class OTAServerTemplate(ABC):  # pylint: disable=too-few-public-methods
    """Abstract base class for OTA server device."""

    @property
    @abstractmethod
    def console(self) -> BoardfarmPexpect:
        """Returns OTA server device console.

        :return: console
        :rtype: BoardfarmPexpect
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def config(self) -> dict:
        """Device configuration.

        :raises NotImplementedError: if not implemented
        :return: device configuration
        :rtype: dict
        """
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError

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
        raise NotImplementedError
