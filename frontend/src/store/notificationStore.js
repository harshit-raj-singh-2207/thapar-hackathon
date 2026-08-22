import { create } from 'zustand';
import { communityApi } from '../services/api/communityApi';
import chatSocket from '../services/websocket/chatSocket';
import { playNotificationSound, playSoundFromUrl } from '../utils/soundEffects';

export const useNotificationStore = create((set, get) => ({
  notifications: [],
  unreadCount: 0,
  loading: false,
  error: null,

  fetchNotifications: async () => {
    set({ loading: true, error: null });
    try {
      const data = await communityApi.getNotifications();
      const notifs = Array.isArray(data) ? data : [];
      const unread = notifs.filter((n) => !n.read).length;
      set({ notifications: notifs, unreadCount: unread, loading: false });
      return notifs;
    } catch (err) {
      set({ error: err.detail || err.message, loading: false });
      return [];
    }
  },

  fetchUnreadCount: async () => {
    try {
      const res = await communityApi.getUnreadNotificationsCount();
      const count = typeof res?.count === 'number' ? res.count : 0;
      set({ unreadCount: count });
      return count;
    } catch (err) {
      console.warn('Failed to fetch unread count:', err);
    }
  },

  markAsRead: async (notificationId) => {
    // Optimistic UI update
    set((state) => {
      let wasUnread = false;
      const updated = state.notifications.map((n) => {
        if (n.id === notificationId) {
          if (!n.read) wasUnread = true;
          return { ...n, read: true };
        }
        return n;
      });
      return {
        notifications: updated,
        unreadCount: wasUnread ? Math.max(0, state.unreadCount - 1) : state.unreadCount,
      };
    });

    try {
      await communityApi.markNotificationRead(notificationId);
    } catch (err) {
      console.error('Failed to mark notification as read:', err);
      get().fetchNotifications();
    }
  },

  markAllAsRead: async () => {
    // Optimistic UI update
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, read: true })),
      unreadCount: 0,
    }));

    try {
      await communityApi.markAllNotificationsRead();
    } catch (err) {
      console.error('Failed to mark all notifications as read:', err);
      get().fetchNotifications();
    }
  },

  handleIncomingNotification: (notifPayload) => {
    if (!notifPayload) return;
    const item = notifPayload.data || notifPayload;
    if (!item.id) {
      item.id = `notif-ws-${Date.now()}`;
    }
    if (!item.created_at) {
      item.created_at = new Date().toISOString();
    }

    // Play notification sound audio effect
    if (item.sound_url) {
      playSoundFromUrl(item.sound_url, item.sound || 'notification');
    } else {
      playNotificationSound();
    }

    set((state) => {
      if (state.notifications.some((n) => n.id === item.id)) {
        return state;
      }
      return {
        notifications: [item, ...state.notifications],
        unreadCount: state.unreadCount + 1,
      };
    });
  },

  initWebSocket: () => {
    chatSocket.connect();
    return chatSocket.addListener((data) => {
      if (data && data.type === 'notification') {
        get().handleIncomingNotification(data.data || data);
      }
    });
  },
}));

export default useNotificationStore;
