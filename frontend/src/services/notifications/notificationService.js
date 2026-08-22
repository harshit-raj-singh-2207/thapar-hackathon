import { communityApi } from '../api/communityApi';
import { useNotificationStore } from '../../store/notificationStore';

export const notificationService = {
  getNotifications: () => communityApi.getNotifications(),
  getUnreadCount: () => communityApi.getUnreadNotificationsCount(),
  markAsRead: (id) => useNotificationStore.getState().markAsRead(id),
  markAllAsRead: () => useNotificationStore.getState().markAllAsRead(),
};

export default notificationService;
