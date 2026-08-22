import storage from '../storage/asyncStorage';
import { WS_URL } from '../../constants/config';

export class WebSocketClient {
  constructor(endpoint = '/community/ws') {
    this.endpoint = endpoint;
    this.ws = null;
    this.listeners = new Set();
  }

  async connect() {
    const token = await storage.getItem('userToken');
    if (!token || this.ws) return;

    const wsUrl = `${WS_URL}${this.endpoint}?token=${token}`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log(`WebSocketClient connected to ${this.endpoint}`);
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.notify(data);
      } catch (e) {
        console.error('Error parsing WS message:', e);
      }
    };

    this.ws.onclose = () => {
      this.ws = null;
    };
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  addListener(cb) {
    this.listeners.add(cb);
    return () => this.listeners.delete(cb);
  }

  notify(data) {
    this.listeners.forEach((cb) => cb(data));
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export default WebSocketClient;
