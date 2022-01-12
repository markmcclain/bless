from enum import Enum

from typing import List, Dict, TYPE_CHECKING

from dbus_next.service import ServiceInterface, method, dbus_property

if TYPE_CHECKING:
    from bless.backends.bluezdbus.dbus.application import (  # type: ignore
        BlueZGattApplication,
    )


class Type(Enum):
    BROADCAST = "broadcast"
    PERIPHERAL = "peripheral"


class BlueZLEAdvertisement(ServiceInterface):
    """
    org.bluez.LEAdvertisement1 interface implementation
    """

    interface_name: str = "org.bluez.LEAdvertisement1"

    def __init__(
        self,
        advertising_type: Type,
        index: int,
        app: "BlueZGattApplication",  # noqa: F821
    ):
        """
        New Low Energy Advertisement

        Parameters
        ----------
        advertising_type : Type
            The type of advertisement
        index : int,
            The index of the advertisement
        app : BlueZGattApplication
            The Application that is responsible for this advertisement
        """
        self.path = app.base_path + "/advertisement" + str(index)

        self._type: str = advertising_type.value
        self._service_uuids: List[str] = []
        self._manufacturer_data: Dict = {}
        self._solicit_uuids: List[str] = [""]
        self._service_data: Dict = {}

        self._include_tx_power: bool = False

        self.data = None
        super(BlueZLEAdvertisement, self).__init__(self.interface_name)

    @method()
    def Release(self):  # noqa: N802
        print("%s: Released!" % self.path)

    @dbus_property()
    def Type(self) -> "s":  # type: ignore # noqa: F821
        return self._type

    @Type.setter  # type: ignore
    def Type(self, type: "s"):  # type: ignore # noqa: F821 F722
        self._type = type

    @dbus_property()
    def ServiceUUIDs(self) -> "as":  # type: ignore # noqa: F821 F722
        return self._service_uuids

    @ServiceUUIDs.setter  # type: ignore
    def ServiceUUIDs(self, service_uuids: "as"):  # type: ignore # noqa: F821 F722
        self._service_uuids = service_uuids

    @dbus_property()
    def ManufacturerData(self) -> "a{qv}":  # type: ignore # noqa: F821 F722
        return self._manufacturer_data

    @ManufacturerData.setter  # type: ignore
    def ManufacturerData(self, data: "a{qv}"):  # type: ignore # noqa: F821 F722
        self._manufacturer_data = data

    # @dbus_property()
    # def SolicitUUIDs(self) -> "as":  # type: ignore # noqa: F821 F722
        # return self._solicit_uuids

    # @SolicitUUIDs.setter  # type: ignore
    # def SolicitUUIDs(self, uuids: "as"):  # type: ignore # noqa: F821 F722
        # self._solicit_uuids = uuids

    @dbus_property()
    def ServiceData(self) -> "a{sv}":  # type: ignore # noqa: F821 F722
        return self._service_data

    @ServiceData.setter  # type: ignore
    def ServiceData(self, data: "a{sv}"):  # type: ignore # noqa: F821 F722
        self._service_data = data

    @dbus_property()
    def IncludeTxPower(self) -> "b":  # type: ignore # noqa: F821
        return self._include_tx_power

    @IncludeTxPower.setter  # type: ignore
    def IncludeTxPower(self, include: "b"):  # type: ignore # noqa: F821
        self._include_tx_power = include
