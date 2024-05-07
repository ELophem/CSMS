// WebSocketService.js
const webSocketService = {
    socket: null,
    listeners: [],
  
    connect(clientId) {
      this.socket = new WebSocket(`ws://localhost:9000/${clientId}`, 'ocpp2.0.1');
      this.socket.onopen = () => {
        console.log('WebSocket connection to CSMS established.');
      };
      this.socket.onclose = () => {
        console.log('WebSocket connection to CSMS closed.');
        // Call any additional cleanup logic if needed
      };
      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      this.socket.onmessage = (event) => {
        console.log('WebSocket message received:', event.data);
        this.listeners.forEach(listener => {
          if (typeof listener === 'function') {
            listener(event);
          }
        });
      };
    },
  
    addEventListener(listener) {
      this.listeners.push(listener);
    },
  
    removeEventListener(listener) {
      this.listeners = this.listeners.filter(l => l !== listener);
    },
  
    send(data) {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.send(data);
      } else {
        console.error('WebSocket connection not established or closed. Unable to send data.');
      }
    },
  
    close() {
      if (this.socket) {
        this.socket.close();
      }
    }
  };
  
  export default webSocketService;
  