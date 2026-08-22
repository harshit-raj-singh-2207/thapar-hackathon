import storage from '../storage/asyncStorage';
import { WS_URL } from '../../constants/config';

class ChatSocketService {
  constructor() {
    this.ws = null;
    this.listeners = new Set();
    this.pingInterval = null;
    this.reconnectTimeout = null;
    this.isExplicitlyClosed = false;
  }

  async connect() {
    const token = await storage.getItem('userToken');
    if (!token || (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING))) return;

    this.isExplicitlyClosed = false;
    const wsUrl = `${WS_URL}/community/ws?token=${token}`;
    try {
      this.ws = new WebSocket(wsUrl);
    } catch (err) {
      console.error('Failed to create WebSocket:', err);
      this.scheduleReconnect();
      return;
    }

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.clearReconnect();
      this.startPing();
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.notifyListeners(data);
      } catch (err) {
        console.error('Error parsing WebSocket message:', err);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket closed');
      this.stopPing();
      this.ws = null;
      if (!this.isExplicitlyClosed) {
        this.scheduleReconnect();
      }
    };
  }

  scheduleReconnect() {
    if (this.reconnectTimeout || this.isExplicitlyClosed) return;
    this.reconnectTimeout = setTimeout(() => {
      this.reconnectTimeout = null;
      this.connect();
    }, 3000);
  }

  clearReconnect() {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
  }

  disconnect() {
    this.isExplicitlyClosed = true;
    this.clearReconnect();
    this.stopPing();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  startPing() {
    this.stopPing();
    this.pingInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000);
  }

  stopPing() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  sendDirectMessage(chatId, text, imageUrl = null) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          type: 'direct_message',
          chat_id: chatId,
          text,
          image_url: imageUrl,
        })
      );
    }
  }

  sendMarkRead(chatId, messageIds = []) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          type: 'mark_read',
          chat_id: chatId,
          conversation_id: chatId,
          message_ids: messageIds,
        })
      );
    }
  }

  sendTypingStart(chatId, recipientId = null, groupId = null) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          type: 'typing_start',
          chat_id: chatId,
          recipient_id: recipientId,
          group_id: groupId,
        })
      );
    }
  }

  sendTypingStop(chatId, recipientId = null, groupId = null) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          type: 'typing_stop',
          chat_id: chatId,
          recipient_id: recipientId,
          group_id: groupId,
        })
      );
    }
  }

  addListener(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  notifyListeners(data) {
    this.listeners.forEach((callback) => {
      try {
        callback(data);
      } catch (err) {
        console.error('Listener callback error:', err);
      }
    });
  }
}

export default new ChatSocketService();

