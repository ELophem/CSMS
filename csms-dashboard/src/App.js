import React from 'react';
import './App.css';

import ChargingPoints from './ChargingPoints';

function App() {
  return (
    <div className="App">
      <header>
        <h1>Electric Vehicle Charging Stations</h1>
      </header>
      <ChargingPoints />
    </div>
  );
}

export default App;
