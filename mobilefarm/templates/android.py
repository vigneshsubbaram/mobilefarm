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
