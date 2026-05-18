"""MobileFarm Android Test Station template."""

from abc import ABC, abstractmethod

from boardfarm3.lib.boardfarm_pexpect import BoardfarmPexpect


class ATSTemplate(ABC):  # pylint: disable=too-few-public-methods
    """Abstract base class for Android Test Station device."""

    @property
    @abstractmethod
    def console(self) -> BoardfarmPexpect:
        """Returns Android Test Station console.

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
