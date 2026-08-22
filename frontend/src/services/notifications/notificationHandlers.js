import { useNotificationStore } from '../../store/notificationStore';

export function handleIncomingNotification(eventData) {
  if (!eventData) return;
  useNotificationStore.getState().handleIncomingNotification(eventData);
}

export default {
  handleIncomingNotification,
};
