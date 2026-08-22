import { create } from 'zustand';
import { communityApi } from '../services/api/communityApi';
import chatSocket from '../services/websocket/chatSocket';

export const useChatStore = create((set, get) => ({
  chats: [],
  activeChatId: null,
  messages: {}, // { [chatId or groupId]: Message[] }
  typingUsers: {}, // { [chatId or groupId]: boolean }
  groupMembers: {}, // { [groupId]: Member[] }
  loading: false,
  error: null,

  fetchChats: async () => {
    set({ loading: true, error: null });
    try {
      const chats = await communityApi.getMyChats();
      set({ chats, loading: false });
    } catch (err) {
      set({ error: err.detail || err.message, loading: false });
    }
  },

  startChat: async (recipientId) => {
    try {
      const chat = await communityApi.createOrGetChat(recipientId);
      await get().fetchChats();
      return chat;
    } catch (err) {
      throw err;
    }
  },

  fetchMessages: async (chatId) => {
    try {
      const chatMsgs = await communityApi.getChatMessages(chatId);
      set((state) => ({
        messages: { ...state.messages, [chatId]: chatMsgs },
      }));
    } catch (err) {
      console.error('Error fetching chat messages:', err);
    }
  },

  sendDirectMessage: async (chatId, { text, image_url }) => {
    try {
      const newMsg = await communityApi.sendChatMessage(chatId, { text, image_url });
      set((state) => {
        const currentList = state.messages[chatId] || [];
        if (currentList.some((m) => m.id === newMsg.id)) return state;
        return {
          messages: {
            ...state.messages,
            [chatId]: [...currentList, newMsg],
          },
        };
      });
      return newMsg;
    } catch (err) {
      throw err;
    }
  },

  fetchGroupMessages: async (groupId) => {
    try {
      const gMsgs = await communityApi.getGroupMessages(groupId);
      set((state) => ({
        messages: { ...state.messages, [groupId]: gMsgs },
      }));
    } catch (err) {
      console.error('Error fetching group messages:', err);
    }
  },

  sendGroupMessage: async (groupId, { text, image_url }) => {
    try {
      const newMsg = await communityApi.sendGroupMessage(groupId, { text, image_url });
      set((state) => {
        const currentList = state.messages[groupId] || [];
        if (currentList.some((m) => m.id === newMsg.id)) return state;
        return {
          messages: {
            ...state.messages,
            [groupId]: [...currentList, newMsg],
          },
        };
      });
      return newMsg;
    } catch (err) {
      throw err;
    }
  },

  markChatRead: async (chatId) => {
    try {
      chatSocket.sendMarkRead(chatId);
      await communityApi.markChatRead(chatId);
    } catch (err) {
      console.error('Error marking chat as read:', err);
    }
  },

  fetchGroupMembers: async (groupId) => {
    try {
      const members = await communityApi.getGroupMembers(groupId);
      set((state) => ({
        groupMembers: { ...state.groupMembers, [groupId]: members },
      }));
    } catch (err) {
      console.error('Error fetching group members:', err);
    }
  },

  initWebSocket: () => {
    chatSocket.connect();
    return chatSocket.addListener((data) => {
      if (!data) return;
      const { type, sender_id, chat_id, conversation_id, group_id, text, attachment_url, id, message_id, status, created_at, user_id, is_online, message_ids } = data;
      const targetId = chat_id || conversation_id || group_id;

      if ((type === 'direct_message' || type === 'group_message' || type === 'message') && targetId) {
        set((state) => {
          const currentList = state.messages[targetId] || [];
          if (currentList.some((m) => m.id === id)) return state;
          const newMsg = {
            id: id || `ws-${Date.now()}`,
            conversation_id: targetId,
            group_id: targetId,
            sender_id,
            text,
            attachment_url,
            status: status || 'delivered',
            created_at: created_at || new Date().toISOString(),
            is_own: false,
          };
          const updatedChats = state.chats.map((c) =>
            c.id === targetId
              ? { ...c, last_message: text || 'Attachment', last_message_at: newMsg.created_at }
              : c
          );
          return {
            messages: {
              ...state.messages,
              [targetId]: [...currentList, newMsg],
            },
            chats: updatedChats,
          };
        });
      } else if (type === 'message_sent_ack' && targetId) {
        set((state) => {
          const currentList = state.messages[targetId] || [];
          return {
            messages: {
              ...state.messages,
              [targetId]: currentList.map((m) =>
                m.id === message_id ? { ...m, status: status || 'sent' } : m
              ),
            },
          };
        });
      } else if (type === 'message_delivered' && targetId) {
        set((state) => {
          const currentList = state.messages[targetId] || [];
          return {
            messages: {
              ...state.messages,
              [targetId]: currentList.map((m) =>
                m.id === message_id ? { ...m, status: 'delivered' } : m
              ),
            },
          };
        });
      } else if (type === 'message_read' && targetId) {
        set((state) => {
          const currentList = state.messages[targetId] || [];
          const idsSet = Array.isArray(message_ids) && message_ids.length > 0 ? new Set(message_ids) : null;
          return {
            messages: {
              ...state.messages,
              [targetId]: currentList.map((m) => {
                if (idsSet) {
                  return idsSet.has(m.id) ? { ...m, status: 'read' } : m;
                }
                return m.is_own ? { ...m, status: 'read' } : m;
              }),
            },
          };
        });
      } else if (type === 'presence_change' && user_id) {
        set((state) => ({
          chats: state.chats.map((c) =>
            c.recipient_id === user_id ? { ...c, is_online } : c
          ),
        }));
      } else if (type === 'typing_start' && targetId) {
        set((state) => ({
          typingUsers: { ...state.typingUsers, [targetId]: true },
        }));
      } else if (type === 'typing_stop' && targetId) {
        set((state) => ({
          typingUsers: { ...state.typingUsers, [targetId]: false },
        }));
      }
    });
  },
}));

