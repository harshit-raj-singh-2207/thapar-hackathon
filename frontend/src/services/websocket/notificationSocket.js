import { WebSocketClient } from './websocketClient';

class NotificationSocketService extends WebSocketClient {
  constructor() {
    super('/community/ws');
  }
}

export default new NotificationSocketService();
