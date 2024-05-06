import asyncio

from ocpp.v201.enums import RegistrationStatusType
import logging
import websockets

from ocpp.v201 import call
from ocpp.routing import on
from ocpp.v201 import call_result
from ocpp.v201 import ChargePoint as cp1

logging.basicConfig(level=logging.INFO)


class ChargePoint(cp1):
    async def send_heartbeat(self, interval):
        request = call.Heartbeat()
        while True:
            await self.call(request)
            await asyncio.sleep(interval)

    async def send_boot_notification(self):
        request = call.BootNotification(
            reason="PowerUp",
            charging_station={
                'model': 'Wallbox XYZ',
                'vendor_name': 'anewone'
            }
        )
        response = await self.call(request)

        if response.status == RegistrationStatusType.accepted:
            print("Connected to central system.")
            await self.send_heartbeat(response.interval)
    

    async def send_meter_values(self):
        request = call.MeterValues(
            evse_id=1,
            meter_value=[
            {
            "timestamp": "2024-05-07T00:00:00Z",
            "sampledValue": [
                {
                "value": 100.5,
                "measurand": "Energy.Active.Import.Register",
                "unitOfMeasure": {
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
        response = await self.call(request)
    
    async def send_status_notification(self):
        request = call.StatusNotification(

        timestamp="2024-05-07T12:34:56Z",  
        connector_status="Available",  
        evse_id=1,  
        connector_id=1  

        )
        response = await self.call(request)
    
    @on("StatusNotification")
    def on_status_notification(self, **kwargs):
        print("Received StatusNotification from CSMS:", kwargs)
       
        timestamp = kwargs.get('timestamp')
        connector_status = kwargs.get('connectorStatus')
        evse_id = kwargs.get('evseId')
        connector_id = kwargs.get('connectorId')

        # Add the logic to handle the status notification from the CSMS
        return call_result.StatusNotification()




 




async def main():
    async with websockets.connect(
            'ws://localhost:9000/CP_1',
            subprotocols=['ocpp2.0.1']
    ) as ws:
        cp1 = ChargePoint('CP_1', ws)

        await asyncio.gather(cp1.start(), cp1.send_boot_notification(),  cp1.send_status_notification(), cp1.send_meter_values())
        

        
if __name__ == '__main__':
    asyncio.run(main())