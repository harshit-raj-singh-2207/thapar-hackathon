import { useEffect, useRef, useState, useCallback } from 'react';
import chatSocket from '../services/websocket/chatSocket';

export const useWebSocket = (urlOrCallback) => {
  const [isReady, setIsReady] = useState(false);
  const [val, setVal] = useState(null);
  const ws = useRef(null);

  useEffect(() => {
    // If a direct URL string is passed
    if (typeof urlOrCallback === 'string' && urlOrCallback) {
      const socket = new WebSocket(urlOrCallback);

      socket.onopen = () => setIsReady(true);
      socket.onclose = () => setIsReady(false);
      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setVal(data);
        } catch (e) {
          setVal(event.data);
        }
      };
      socket.onerror = (error) => console.error("WS Error:", error);

      ws.current = socket;

      return () => {
        socket.close();
      };
    }

    // Default chatSocket subscription mode
    chatSocket.connect();
    setIsReady(true);

    let unsubscribe;
    if (typeof urlOrCallback === 'function') {
      unsubscribe = chatSocket.addListener((data) => {
        setVal(data);
        urlOrCallback(data);
      });
    }

    return () => {
      if (unsubscribe) unsubscribe();
    };
  }, [urlOrCallback]);

  const sendData = useCallback((data) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(data));
    } else {
      chatSocket.send(data);
    }
  }, []);

  return {
    isReady,
    isConnected: isReady,
    val,
    sendData,
    sendTypingStart: (chatId, recipientId, groupId) => chatSocket.sendTypingStart(chatId, recipientId, groupId),
    sendTypingStop: (chatId, recipientId, groupId) => chatSocket.sendTypingStop(chatId, recipientId, groupId),
  };
};

export default useWebSocket;
