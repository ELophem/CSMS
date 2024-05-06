import React, { useState, useEffect } from 'react';

const ChargingPoints = () => {
  const [connected1, setConnected1] = useState(false);
  const [connected2, setConnected2] = useState(false);

  useEffect(() => {
    const socket1 = new WebSocket('ws://localhost:9000/CP_1', 'ocpp2.0.1');
    const socket2 = new WebSocket('ws://localhost:9000/CP_2', 'ocpp2.0.1');

    socket1.onopen = () => {
      console.log('WebSocket connection to CP_1 established.');
      setConnected1(true);
    };

    socket1.onclose = () => {
      console.log('WebSocket connection to CP_1 closed.');
      setConnected1(false);
    };

    socket1.onerror = (error) => {
      console.error('WebSocket error on CP_1:', error);
      setConnected1(false);
    };

    socket2.onopen = () => {
      console.log('WebSocket connection to CP_2 established.');
      setConnected2(true);
    };

    socket2.onclose = () => {
      console.log('WebSocket connection to CP_2 closed.');
      setConnected2(false);
    };

    socket2.onerror = (error) => {
      console.error('WebSocket error on CP_2:', error);
      setConnected2(false);
    };

    return () => {
      socket1.close();
      socket2.close();
    };
  }, []);

  return (
    <div>
      <h1>WebSocket Connection Status</h1>
      <p>CP_1: {connected1 ? 'Connected' : 'Disconnected'}</p>
      <p>CP_2: {connected2 ? 'Connected' : 'Disconnected'}</p>
    </div>
  );
};

export default ChargingPoints;