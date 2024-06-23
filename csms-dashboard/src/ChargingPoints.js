import React, { useState, useEffect } from 'react';
import webSocketService from './WebSocketService';

const formatTime = (timestamp) => {
  const date = new Date(timestamp);
  const day = date.getDate().toString().padStart(2, '0');
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const year = date.getFullYear();
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  const seconds = date.getSeconds().toString().padStart(2, '0');
  return `${day}-${month}-${year} ${hours}:${minutes}:${seconds}`;
};

const ChargingPoints = () => {
  const [chargingStations, setChargingStations] = useState({});
  const [totalConsumed, setTotalConsumed] = useState(0);

  useEffect(() => {
    const clientId = "RC_123"; 
    webSocketService.connect(clientId);

    const listener = (event) => {
      if (event && event.data) {
        console.log('Received message:', event.data);
        try {
          const data = JSON.parse(event.data);
          if (data.messageType === "Heartbeat") {
            const stationId = data.chargePointId;
            console.log('Received Heartbeat message. Updating charging station:', stationId);
            setChargingStations(prevStations => ({
              ...prevStations,
              [stationId]: { ...prevStations[stationId], id: stationId, connected: true },
            }));
          } else if (data.messageType === "MeterValues") {
            const { stationId, meterValues } = data;
            console.log('Received MeterValues message. Updating charging station:', stationId);
            const updatedStations = {
              ...chargingStations,
              [stationId]: {
                ...chargingStations[stationId],
                meterValues: meterValues.map(value => ({
                  timestamp: value.timestamp,
                  value: value.sampled_value[0].value,
                  unitOfMeasure: value.sampled_value[0].unit_of_measure.unit
                }))
              }
            };
            setChargingStations(updatedStations);

            // Calculate total consumed energy
            let total = 0;
            Object.values(updatedStations).forEach(station => {
              if (station.meterValues) {
                station.meterValues.forEach(value => {
                  total += value.value;
                });
              }
            });
            setTotalConsumed(total);
          } else if (data.messageType === "StatusNotification") {
            const { stationId, connectorStatus } = data;
            console.log('Received StatusNotification message. Updating charging station:', stationId);
            setChargingStations(prevStations => ({
              ...prevStations,
              [stationId]: { ...prevStations[stationId], id: stationId, connectorStatus },
            }));
          }
        } catch (error) {
          console.error('Error parsing message:', error);
        }
      }
    };

    webSocketService.addEventListener(listener);

    return () => {
      webSocketService.removeEventListener(listener);
    };
  }, [chargingStations]);

//  const getTransactionIdForStation = (stationId) => {
//    const station = chargingStations[stationId];
//   return station && station.transactionId ? station.transactionId : null;
//  };

  const handleStopTransaction = (stationId) => {
    const stopTransactionRequest = {
      messageType: 'StopTransaction',
      transactionId: stationId, 
    };
  
    console.log('Sending stop transaction request:', stopTransactionRequest); 
    webSocketService.send(stopTransactionRequest); 
  };
  

  console.log('Charging stations:', chargingStations);

  return (
    <div>
      <h2>Active Charging Stations</h2>
      <div style={{ display: 'flex', flexWrap: 'wrap' }}>
      {Object.values(chargingStations).map(station => (
  <div key={station.id} style={{ border: '1px solid black', padding: '10px', margin: '10px' }}>
    <h3>Charge Point: {station.id}</h3>
    <p>Status of charging pole: {station.connected ? 'Connected' : 'Disconnected'}</p>
    <p>Connector Status: {station.connectorStatus}</p>
    {station.meterValues && (
      <div>
        {station.meterValues.map((value, index) => (
          <div key={index}> {/* Use index as key temporarily */}
            <p>Timestamp: {formatTime(value.timestamp)}</p>
            <p>Value: {value.value} {value.unitOfMeasure}</p>
          </div>
        ))}
      </div>
    )}
    <button onClick={() => handleStopTransaction(station.id)}>Stop Transaction</button>
  </div>
))}

      </div>
      <h3>Total Consumed Energy: {totalConsumed} kW</h3>
    </div>
  );
};

export default ChargingPoints;
