import asyncio
import logging
import websockets
import json
from datetime import datetime

from ocpp.routing import on
from ocpp.v201 import ChargePoint as cp
from ocpp.v201 import call_result
from ocpp.v201.enums import RegistrationStatusType

logging.basicConfig(level=logging.INFO)

# Maintain dictionaries to store connected clients
connected_charge_points = {}
connected_react_clients = {}

async def forward_message_to_react_clients(message):
    # Forward the received message to all connected React clients
    for rc_ws in connected_react_clients.values():
        await rc_ws.send(message)

class ChargePoint(cp):
    @on('BootNotification')
    async def on_boot_notification(self, charging_station, reason, **kwargs):
        return call_result.BootNotification(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status=RegistrationStatusType.accepted
        )

    @on("Heartbeat")
    async def on_heartbeat(self):
        charge_point_id = self.id
        logging.info(f"Received Heartbeat from Charge Point {charge_point_id}")
        # Forward heartbeat notification with charge point ID to React clients
        for rc_ws in connected_react_clients.values():
            await rc_ws.send('{"messageType": "Heartbeat", "chargePointId": "' + charge_point_id + '"}')
        return call_result.Heartbeat(
            current_time=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        )

    @on("MeterValues")
    async def on_meter_values(self, evse_id, meter_value, **kwargs):
        logging.info(f"Received MeterValues from Charge Point {self.id}:")
        logging.info(f"EVSE ID: {evse_id}")
        logging.info(f"meter_value: {meter_value}")
        
        json_data = {
            "messageType" : "MeterValues",
            "stationId": self.id,
            "meterValues": meter_value
        }
        

        json_string = json.dumps(json_data)
        
        # Forward the message to React clients
        await forward_message_to_react_clients(json_string)
        
        return call_result.MeterValues()
    
    @on("StatusNotification")
    async def on_status_notification(self, timestamp, connector_status, evse_id, connector_id, **kwargs):
        logging.info(f"Received StatusNotification from Charge Point {self.id}")
        logging.info(f"Timestamp: {timestamp}, Status: {connector_status}, EVSE ID: {evse_id}, Connector ID: {connector_id}")

        json_data = {
            "messageType": "StatusNotification",
            "stationId": self.id,
            "timestamp": timestamp,
            "connectorStatus": connector_status,
            "evseId": evse_id,
            "connectorId": connector_id
        }

        json_string = json.dumps(json_data)
        
        # Forward the message to React clients
        await forward_message_to_react_clients(json_string)

        return call_result.StatusNotification()

    @on("StopTransaction")
    async def on_stop_transaction(self):
        return call_result.RequestStopTransaction()
        

async def on_connect(websocket, path):
    try:
        requested_protocols = websocket.request_headers['Sec-WebSocket-Protocol']
    except KeyError:
        logging.info("Client hasn't requested any Subprotocol. Closing Connection")
        return await websocket.close()

    if websocket.subprotocol:
        logging.info("Protocols Matched: %s", websocket.subprotocol)
    else:
        logging.warning('Protocols Mismatched | Expected Subprotocols: %s,'
                        ' but client supports  %s | Closing connection',
                        websocket.available_subprotocols,
                        requested_protocols)
        return await websocket.close()

    # Extract client type and client ID from the path
    path_components = path.strip('/').split('_')
    if len(path_components) != 2:
        logging.error("Invalid path format. Closing connection.")
        return await websocket.close()

    client_type, client_id = path_components

    if client_type == 'CP':  # Charging point client
        cp_instance = ChargePoint(client_id, websocket)
        connected_charge_points[client_id] = cp_instance
        await cp_instance.start()
    elif client_type == 'RC':  # React client
        connected_react_clients[client_id] = websocket
        logging.info(f"React client connected: {client_id}")

    while True:
        try:
            message = await websocket.recv()
            sender_client_id = client_id if client_type == 'CP' else f"RC_{client_id}"
            if client_type == 'CP':
                # Forward message to React clients
                for rc_ws in connected_react_clients.values():
                    await rc_ws.send(f"From CP {sender_client_id}: {message}")
            else:  # React client
                # Forward message to charging point clients
                cp_id = sender_client_id.split('_')[1]
                cp_ws = connected_charge_points.get(cp_id)
                if cp_ws:
                    await cp_ws.send(f"From RC {sender_client_id}: {message}")
                else:
                    logging.warning(f"No connected charging point found for RC {sender_client_id}")

        except websockets.exceptions.ConnectionClosed:
            if client_type == 'CP':
                logging.info(f"Connection closed for Charge Point: {client_id}")
                del connected_charge_points[client_id]
            elif client_type == 'RC':
                logging.info(f"Connection closed for React client: {client_id}")
                del connected_react_clients[client_id]
            break


async def main():
    server = await websockets.serve(
        on_connect,
        '0.0.0.0',
        9000,
        subprotocols=['ocpp2.0.1']
    )
    logging.info("WebSocket Server Started")
    await server.wait_closed()


if __name__ == '__main__':
    asyncio.run(main())
