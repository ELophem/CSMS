import asyncio
from datetime import datetime, timedelta

from ocpp.v201.enums import RegistrationStatusType
import logging
import websockets

from ocpp.v201 import call
from ocpp.routing import on
from ocpp.v201 import ChargePoint as cp2

logging.basicConfig(level=logging.INFO)


class ChargePoint(cp2):
    async def send_heartbeat(self, interval):
        request = call.Heartbeat()
        while True:
            await self.call(request)
            await asyncio.gather(
                self.send_meter_values(),  # Send meter values
                asyncio.sleep(interval)    # Wait for heartbeat interval
            )


    async def send_boot_notification(self):
        request = call.BootNotification(
            reason="PowerUp",
            charging_station={
                'model': 'Edouard',
                'vendor_name': 'anewone'
            }
        )
        response = await self.call(request)

        if response.status == RegistrationStatusType.accepted:
            print("Connected to central system.")
            await self.send_heartbeat(response.interval)

    # async def send_status_notification(self):
    #     request = call.StatusNotification(
    #         timestamp=datetime.utcnow().isoformat() + "Z",  # Ensure UTC format with 'Z' suffix
    #         connector_status="Available",
    #         evse_id=1,
    #         connector_id=1
    #     )
    #     await self.call(request)

    async def send_meter_values(self):
        request = call.MeterValues(
            evse_id=1,
            meter_value=[
                {
                    "timestamp": datetime.utcnow().isoformat() + "Z",  # Ensure UTC format with 'Z' suffix
                    "sampled_value": [
                        {
                            "value": 300,
                            "measurand": "Energy.Active.Import.Register",
                            "unit_of_measure": {
                                "unit": "Wh",
                                "multiplier": 0
                            },
                            "location": "Outlet",
                            "context": "Sample.Periodic"
                        }
                    ]
                }
            ]
        )
        await self.call(request)


    async def periodic_tasks(self):
        while True:
            await asyncio.gather(
                # self.send_status_notification(),
                self.send_meter_values()
            )
            await asyncio.sleep(60)  # Adjust interval as needed


async def main():
    async with websockets.connect(
            'ws://localhost:9000/CP_2',
            subprotocols=['ocpp2.0.1']
    ) as ws:
        cp2 = ChargePoint('CP_1', ws)

        await asyncio.gather(cp2.start(), cp2.send_boot_notification(), cp2.periodic_tasks())


if __name__ == '__main__':
    asyncio.run(main())
