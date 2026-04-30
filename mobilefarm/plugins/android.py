"""Boardfarm plugin for Android devices."""

from boardfarm3 import hookimpl
from boardfarm3.devices.base_devices import BoardfarmDevice

from mobilefarm.devices.cuttlefish import CuttleFish
from mobilefarm.devices.ota_server import OTAServer
from mobilefarm.devices.pixel8_pro import Pixel8Pro


@hookimpl
def boardfarm_add_devices() -> dict[str, type[BoardfarmDevice]]:
    """Add devices to known devices for deployment.

    :return: devices dictionary
    :rtype: dict[str, type[BoardfarmDevice]]
    """
    return {
        "pixel8_pro": Pixel8Pro,
        "cuttlefish": CuttleFish,
        "ota_server": OTAServer,
    }
