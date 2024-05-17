import asyncio
import json
from datetime import datetime, timezone
from ocpp.v201.enums import RegistrationStatusType
import logging
import websockets
from ocpp.v201 import call
from ocpp.v201 import ChargePoint as cp1
import os

logging.basicConfig(level=logging.INFO)

class ChargePoint(cp1):
    def __init__(self, id, connection):
        super().__init__(id, connection)

    async def send_heartbeat(self, interval):
        request = call.Heartbeat()
        while True:
            await self.call(request)
            await asyncio.gather(
                self.read_config_and_send_values(),  # Read config and send messages
                asyncio.sleep(interval)         # Wait for heartbeat interval
            )

    async def send_boot_notification(self, boot_data):
        request = call.BootNotification(
            reason=boot_data['reason'],
            charging_station=boot_data['charging_station']
        )
        response = await self.call(request)

        if response.status == RegistrationStatusType.accepted:
            print("Connected to central system.")
            await self.send_heartbeat(response.interval)

    async def send_status_notification(self, status_data):
        current_timestamp = datetime.now(timezone.utc).isoformat()
        request = call.StatusNotification(
            timestamp=current_timestamp,
            connector_status=status_data['connector_status'],
            evse_id=status_data['evse_id'],
            connector_id=status_data['connector_id']
        )
        await self.call(request)

    async def send_meter_values(self, meter_data):
        current_timestamp = datetime.now(timezone.utc).isoformat()
        # Update the meter data with the current timestamp
        meter_data['values'][0]['timestamp'] = current_timestamp

        request = call.MeterValues(
            evse_id=meter_data['evse_id'],
            meter_value=[
                {
                    "timestamp": meter_data['values'][0]['timestamp'],
                    "sampled_value": [
                        {
                            "value": meter_data['values'][0]['value'],
                            "measurand": meter_data['values'][0]['measurand'],
                            "unit_of_measure": meter_data['values'][0]['unit_of_measure'],
                            "location": meter_data['values'][0]['location'],
                            "context": meter_data['values'][0]['context']
                        }
                    ]
                }
            ]
        )
        await self.call(request)

    async def read_config_and_send_values(self):
        try:
            config_path = os.path.abspath('config_CP_1.json')
            logging.info(f"Reading configuration from: {config_path}")
            with open(config_path, 'r') as f:
                config = json.load(f)
                status_data = config['status_notification']
                meter_data = config['meter_values']

                # Send status notification based on the config
                await self.send_status_notification(status_data)
                # Send meter values based on the config
                await self.send_meter_values(meter_data)
                    
        except FileNotFoundError:
            logging.error(f"Configuration file not found: {config_path}")
        except Exception as e:
            logging.error(f"Error reading config: {e}")
        
        await asyncio.sleep(10)  # Check for updates every 10 seconds

async def main():
    # Print the current working directory
    cwd = os.getcwd()
    logging.info(f"Current working directory: {cwd}")
    
    # List all files in the current directory
    files = os.listdir(cwd)
    logging.info(f"Files in current directory: {files}")

    config_path = os.path.abspath('config_CP_1.json')  # Ensure this path is correct
    if not os.path.exists(config_path):
        logging.error(f"Configuration file does not exist: {config_path}")
        return

    async with websockets.connect(
            'ws://localhost:9000/CP_1',
            subprotocols=['ocpp2.0.1']
    ) as ws:
        cp1 = ChargePoint('CP_1', ws)

        with open(config_path, 'r') as f:
            config = json.load(f)
            boot_data = config['boot_notification']

        await asyncio.gather(cp1.start(), cp1.send_boot_notification(boot_data))

if __name__ == '__main__':
    asyncio.run(main())
