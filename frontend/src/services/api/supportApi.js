import apiClient from './apiClient';

export const supportApi = {
  getHotlines: () => apiClient.get('/support/hotlines'),
  getMyTickets: () => apiClient.get('/support/tickets'),
  getTicketDetails: (ticketId) => apiClient.get(`/support/tickets/${ticketId}`),
  createTicket: ({ subject, category, description }) =>
    apiClient.post('/support/tickets', { subject, category, description }),
  scheduleCall: ({ time_slot, phone_number }) =>
    apiClient.post('/support/calls/schedule', { time_slot, phone_number }),
  getMyCalls: () => apiClient.get('/support/calls'),
};
