import apiClient from './apiClient';

export const caregiverApi = {
  getChildProfile: (childId = 'child-leo-1') =>
    apiClient.get(`/caregiver/${childId}/profile`),

  getChildStatus: (childId = 'child-leo-1') =>
    apiClient.get(`/caregiver/${childId}/status`),

  getChildLocation: (childId = 'child-leo-1') =>
    apiClient.get(`/caregiver/${childId}/location`),

  getChildDevice: (childId = 'child-leo-1') =>
    apiClient.get(`/caregiver/${childId}/device`),

  getSafetyOverview: (childId = 'child-leo-1') =>
    apiClient.get(`/caregiver/${childId}/safety-overview`),

  getRecentActivity: (childId = 'child-leo-1', limit = 20) =>
    apiClient.get(`/caregiver/${childId}/activity?limit=${limit}`),

  getAlertSummary: (childId = 'child-leo-1') =>
    apiClient.get(`/caregiver/${childId}/alerts`),
};

export default caregiverApi;
