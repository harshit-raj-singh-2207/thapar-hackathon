import apiClient from './apiClient';

export const dashboardApi = {
  getDashboardData: () => apiClient.get('/dashboard'),
  getMyGroupsCount: () => apiClient.get('/groups/my/count'),
  getUnreadMessagesCount: () => apiClient.get('/messages/unread/count'),
  getUnreadNotificationsCount: () => apiClient.get('/notifications/unread/count'),
  getNotifications: () => apiClient.get('/notifications'),
  getOnlineCommunityCount: () => apiClient.get('/community/online/count'),
  getFeedPosts: (limit = 10) => apiClient.get(`/posts/feed?limit=${limit}`),
  createPost: ({ content, category, image_url }) =>
    apiClient.post('/posts', { content, category, image_url }),
  likePost: (postId) => apiClient.post(`/posts/${postId}/like`),
  unlikePost: (postId) => apiClient.delete(`/posts/${postId}/like`),
  savePost: (postId) => apiClient.post(`/posts/${postId}/save`),
  unsavePost: (postId) => apiClient.delete(`/posts/${postId}/save`),
  getUpcomingEvents: (limit = 5) => apiClient.get(`/events/upcoming?limit=${limit}`),
  getSuggestedGroups: (limit = 5) => apiClient.get(`/groups/suggested?limit=${limit}`),
  joinGroup: (groupId) => apiClient.post(`/groups/${groupId}/join`),
  leaveGroup: (groupId) => apiClient.delete(`/groups/${groupId}/leave`),
  getCaregiverSpotlight: () => apiClient.get('/caregivers/spotlight'),
  search: (query) => apiClient.get(`/search?query=${encodeURIComponent(query)}`),
};

export default dashboardApi;
