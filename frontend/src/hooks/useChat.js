import { useEffect } from 'react';
import { useChatStore } from '../store/chatStore';

export function useChat(chatId = null, groupId = null) {
  const {
    chats,
    messages,
    typingUsers,
    groupMembers,
    loading,
    error,
    fetchChats,
    startChat,
    fetchMessages,
    sendDirectMessage,
    fetchGroupMessages,
    sendGroupMessage,
    fetchGroupMembers,
    initWebSocket,
  } = useChatStore();

  useEffect(() => {
    fetchChats();
    const cleanupWs = initWebSocket();
    return () => cleanupWs && cleanupWs();
  }, []);

  useEffect(() => {
    if (chatId) fetchMessages(chatId);
  }, [chatId]);

  useEffect(() => {
    if (groupId) {
      fetchGroupMessages(groupId);
      fetchGroupMembers(groupId);
    }
  }, [groupId]);

  return {
    chats,
    messages: chatId ? messages[chatId] || [] : groupId ? messages[groupId] || [] : [],
    typingUsers,
    groupMembers: groupId ? groupMembers[groupId] || [] : [],
    loading,
    error,
    refetchChats: fetchChats,
    startChat,
    sendDirectMessage: (text, image_url) => sendDirectMessage(chatId, { text, image_url }),
    sendGroupMessage: (text, image_url) => sendGroupMessage(groupId, { text, image_url }),
  };
}

export default useChat;
