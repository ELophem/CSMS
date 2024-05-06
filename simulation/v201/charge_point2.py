import asyncio

from ocpp.v201.enums import RegistrationStatusType
import logging
import websockets

from ocpp.v201 import call
from ocpp.v201 import ChargePoint as cp2

logging.basicConfig(level=logging.INFO)


class ChargePoint(cp2):
    async def send_heartbeat(self, interval):
        request = call.HeartbeatPayload()
        while True:
            await self.call(request)
            await asyncio.sleep(interval)

    async def send_boot_notification(self):
        request = call.BootNotificationPayload(
            reason="PowerUp",
            charging_station={
                'model': 'test',
                'vendor_name': 'edouard'
            }
        )
        response = await self.call(request)

        if response.status == RegistrationStatusType.accepted:
            print("Connected to central system.")
            await self.send_heartbeat(response.interval)


async def main():
    async with websockets.connect(
            'ws://localhost:9000/CP_2',
            subprotocols=['ocpp2.0.1']
    ) as ws:
        cp2 = ChargePoint('CP_2', ws)

        await asyncio.gather(cp2.start(), cp2.send_boot_notification())


if __name__ == '__main__':
    asyncio.run(main())