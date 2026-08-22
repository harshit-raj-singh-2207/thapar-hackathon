import apiClient from './apiClient';

export const learningApi = {
  getRoutines: async () => {
    return apiClient.get('/learning/routines');
  },

  createRoutine: async (routineData) => {
    return apiClient.post('/learning/routines', routineData);
  },

  toggleRoutineStep: async (stepId) => {
    return apiClient.post(`/learning/routines/steps/${stepId}/toggle`);
  },

  resetRoutine: async (routineId) => {
    return apiClient.post(`/learning/routines/${routineId}/reset`);
  },

  breakdownTaskAI: async (taskTitle, customContext = null) => {
    return apiClient.post('/learning/breakdown-task', {
      task_title: taskTitle,
      custom_context: customContext,
    });
  },

  getTasks: async () => {
    return apiClient.get('/learning/tasks');
  },

  createTask: async (taskData) => {
    return apiClient.post('/learning/tasks', taskData);
  },

  updateTaskStep: async (taskId, stepIndex, isCompleted) => {
    return apiClient.post(
      `/learning/tasks/${taskId}/steps/${stepIndex}?is_completed=${isCompleted}`
    );
  },

  getReminders: async () => {
    return apiClient.get('/learning/reminders');
  },

  createReminder: async (reminderData) => {
    return apiClient.post('/learning/reminders', reminderData);
  },

  toggleReminder: async (reminderId) => {
    return apiClient.post(`/learning/reminders/${reminderId}/toggle`);
  },

  askTutor: async (question, topic = 'General', sessionId = null) => {
    return apiClient.post('/learning/tutor/ask', {
      question,
      topic,
      session_id: sessionId,
    });
  },

  getTopics: async () => {
    return apiClient.get('/learning/topics');
  },

  updateTopicProgress: async (topicId, progressPct, isCompleted = false) => {
    return apiClient.post(
      `/learning/topics/${topicId}/progress?progress_pct=${progressPct}&is_completed=${isCompleted}`
    );
  },
};

export default learningApi;
