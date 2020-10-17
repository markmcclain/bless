import sys
import uuid
import pytest
import asyncio
import aioconsole

import numpy as np

from typing import Optional, List

from bleaks.backends.characteristic import BleaksGATTCharacteristic

# Eventually should be removed when MacOS, Windows, and Linux are added
if sys.platform not in ['darwin']:
    pytest.skip("Only mac current works", allow_module_level=True)

from bleaks import BleakServer  # noqa: E402
from bleaks.backends.characteristic import (  # noqa: E402
        GattCharacteristicsFlags,
        GATTAttributePermissions
        )

hardware_only = pytest.mark.skipif("os.environ.get('TEST_HARDWARE') is None")


@hardware_only
class TestBleakServer:
    """
    Test specification for bleak server

    This is a hardware dependent test and will only run when the TEST_HARDWARE
    environment variable is set
    """

    def gen_hex_pairs(self) -> str:
        hex_words: List[str] = [
                'DEAD', 'FACE', 'BABE',
                'CAFE', 'FADE', 'BAD',
                'DAD', 'ACE', 'BED'
                ]
        rng: np.random._generator.Generator = np.random.default_rng()
        return ''.join(rng.choice(hex_words, 2, replace=False))

    def hex_to_byte(self, hexstr: str) -> bytearray:
        return bytearray(
                int(f"0x{hexstr}", 16).to_bytes(
                    length=int(np.ceil(len(hexstr)/2)),
                    byteorder="big"
                    )
                )

    def byte_to_hex(self, b: bytearray) -> str:
        return ''.join([hex(x)[2:] for x in b]).upper()

    @pytest.mark.asyncio
    async def test_server(self):
        # Initialize
        server: BleakServer = BleakServer("Test Server")

        # setup a service
        service_uuid: str = str(uuid.uuid4())
        await server.add_new_service(service_uuid)

        assert len(server.services) > 0
        print(server.services)

        # setup a characteristic for the service
        char_uuid: str = str(uuid.uuid4())
        char_flags: GattCharacteristicsFlags = (
                GattCharacteristicsFlags.read |
                GattCharacteristicsFlags.write |
                GattCharacteristicsFlags.notify
                )
        value: Optional[bytearray] = None
        permissions: GATTAttributePermissions = (
                GATTAttributePermissions.readable |
                GATTAttributePermissions.writeable
                )

        await server.add_new_characteristic(
                service_uuid,
                char_uuid,
                char_flags.value,
                value,
                permissions.value
                )

        assert server.services[service_uuid].get_characteristic(char_uuid)

        # Set up read and write callbacks
        def read(characteristic: BleaksGATTCharacteristic) -> bytearray:
            return characteristic.value

        def write(characteristic: BleaksGATTCharacteristic, value: bytearray):
            characteristic.value = value

        server.read_request_func = read
        server.write_request_func = write

        # Start advertising
        assert server.is_advertising() is False

        await server.start()

        assert server.is_advertising() is True

        # Subscribe
        assert server.is_connected() is False

        print(
                "\nPlease connect to the computer and " +
                f"subscribe to characteristic {char_uuid}"
                )
        await aioconsole.ainput("Press enter when ready...")

        assert server.is_connected() is True

        # Read Test
        hex_val: str = self.gen_hex_pairs()
        server.get_characteristic(char_uuid).value = self.hex_to_byte(hex_val)
        print(
                "Trigger a read command and " +
                "enter the capital letters you retrieve below"
                )
        entered_value = await aioconsole.ainput("Value: ")
        assert entered_value == hex_val

        # Write Test
        hex_val = self.gen_hex_pairs()
        print(f"Set the characteristic to this value: {hex_val}")
        await aioconsole.ainput("Press enter when ready...")
        entered_value = self.byte_to_hex(
                server.get_characteristic(char_uuid).value
                )
        assert entered_value == hex_val

        # Notify Test
        hex_val = self.gen_hex_pairs()
        server.get_characteristic(char_uuid).value = self.hex_to_byte(hex_val)

        print("A new value will be notified on the phone")
        await aioconsole.ainput("Press enter to receive the new value...")

        server.update_value(service_uuid, char_uuid)

        new_value: str = await aioconsole.ainput("Enter the new value: ")
        assert new_value == hex_val

        # unsubscribe
        print("Unsubscribe from the characteristic")
        await aioconsole.ainput("Press entery when ready...")
        assert server.is_connected() is False

        # Stop Advertising
        await server.stop()
        await asyncio.sleep(2)
        assert server.is_advertising() is False