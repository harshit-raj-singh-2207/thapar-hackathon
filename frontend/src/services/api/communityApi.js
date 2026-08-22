import apiClient from './apiClient';

export const communityApi = {
  // Caregiver Access, Profiles & Privacy
  checkCommunityAccess: () => apiClient.get('/caregivers/me/community-access'),
  getMyProfile: () => apiClient.get('/caregivers/me/profile'),
  updateMyProfile: ({ bio, avatar_url }) => apiClient.patch('/caregivers/me/profile', { bio, avatar_url }),
  getCaregiverProfile: (userId) => apiClient.get(`/caregivers/${userId}/profile`),
  getPrivacySettings: () => apiClient.get('/caregivers/me/privacy-settings'),
  updatePrivacySettings: (data) => apiClient.patch('/caregivers/me/privacy-settings', data),
  submitVerificationRequest: ({ role_bio, document_notes }) =>
    apiClient.post('/caregivers/me/verification-request', { role_bio, document_notes }),
  getVerificationStatus: () => apiClient.get('/caregivers/me/verification-status'),
  requestDataArchive: () => apiClient.post('/caregivers/me/request-archive'),



  // Direct Chats
  getMyChats: () => apiClient.get('/community/chats'),
  createOrGetChat: (recipientId) => apiClient.post('/community/chats', { recipient_id: recipientId }),
  getChatMessages: (chatId) => apiClient.get(`/community/chats/${chatId}/messages`),
  sendChatMessage: (chatId, { text, image_url }) =>
    apiClient.post(`/community/chats/${chatId}/messages`, { text, image_url }),
  markChatRead: (chatId) => apiClient.post(`/community/chats/${chatId}/read`),


  // Groups
  discoverGroups: (search = '') => apiClient.get(`/community/groups/discover${search ? `?search=${encodeURIComponent(search)}` : ''}`),
  createGroup: ({ name, description, category }) => apiClient.post('/community/groups', { name, description, category }),
  joinGroup: (groupId) => apiClient.post(`/community/groups/${groupId}/join`),
  leaveGroup: (groupId) => apiClient.post(`/community/groups/${groupId}/leave`),
  getGroupMembers: (groupId) => apiClient.get(`/community/groups/${groupId}/members`),
  getGroupMessages: (groupId) => apiClient.get(`/community/groups/${groupId}/messages`),
  sendGroupMessage: (groupId, { text, image_url }) =>
    apiClient.post(`/community/groups/${groupId}/messages`, { text, image_url }),

  // Community Feed Posts
  getPosts: (category = 'All') => apiClient.get(`/community/posts${category && category !== 'All' ? `?category=${encodeURIComponent(category)}` : ''}`),
  createPost: ({ content, image_url, category }) => apiClient.post('/community/posts', { content, image_url, category }),
  getPostDetails: (postId) => apiClient.get(`/community/posts/${postId}`),
  updatePost: (postId, { content, image_url, category }) => apiClient.put(`/community/posts/${postId}`, { content, image_url, category }),
  deletePost: (postId) => apiClient.delete(`/community/posts/${postId}`),
  toggleLikePost: (postId) => apiClient.post(`/community/posts/${postId}/like`),

  // Comments
  getComments: (postId) => apiClient.get(`/community/posts/${postId}/comments`),
  addComment: (postId, content) => apiClient.post(`/community/posts/${postId}/comments`, { content }),
  deleteComment: (postId, commentId) => apiClient.delete(`/community/posts/${postId}/comments/${commentId}`),

  // Community Resources
  getResources: (category = 'All') => apiClient.get(`/community/resources${category && category !== 'All' ? `?category=${encodeURIComponent(category)}` : ''}`),
  getResourceDetails: (resourceId) => apiClient.get(`/community/resources/${resourceId}`),
  createResource: ({ title, description, category, url, file_type }) =>
    apiClient.post('/community/resources', { title, description, category, url, file_type }),
  updateResource: (resourceId, data) => apiClient.put(`/community/resources/${resourceId}`, data),
  deleteResource: (resourceId) => apiClient.delete(`/community/resources/${resourceId}`),


  // Notifications
  getNotifications: () => apiClient.get('/community/notifications'),
  getUnreadNotificationsCount: () => apiClient.get('/community/notifications/unread-count'),
  markNotificationRead: (notificationId) => apiClient.post(`/community/notifications/${notificationId}/read`),
  markAllNotificationsRead: () => apiClient.post('/community/notifications/read-all'),

  // Safety & Uploads
  uploadMedia: (formData) => apiClient.uploadMedia('/community/media/upload', formData),
  submitReport: ({ target_type, target_id, reason }) => apiClient.post('/community/safety/reports', { target_type, target_id, reason }),
  blockCaregiver: (blockedUserId) => apiClient.post('/community/safety/blocks', { blocked_user_id: blockedUserId }),
  getBlockedCaregivers: () => apiClient.get('/community/safety/blocks'),
  unblockCaregiver: (blockedUserId) => apiClient.delete(`/community/safety/blocks/${blockedUserId}`),
};

