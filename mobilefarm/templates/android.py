"""Android device template."""

from abc import ABC, abstractmethod

from boardfarm3.lib.boardfarm_pexpect import BoardfarmPexpect


class AndroidTemplate(ABC):  # pylint: disable=too-few-public-methods
    """Abstract base class for Android devices."""

    @property
    @abstractmethod
    def console(self) -> BoardfarmPexpect:
        """Returns LAN console.

        :return: console
        :rtype: BoardfarmPexpect
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def config(self) -> dict:
        """Device configuration."""
        raise NotImplementedError

    @property
    @abstractmethod
    def app_package(self) -> str:
        """Device app package."""
        raise NotImplementedError

    @property
    @abstractmethod
    def app_activity(self) -> str:
        """Device app activity."""
        raise NotImplementedError
