import apiClient from './apiClient';

export const communicationApi = {
  getAACBoard: async () => {
    return apiClient.get('/communication/aac-board');
  },

  buildSentence: async (tokens, emotion = null, style = 'natural') => {
    return apiClient.post('/communication/build-sentence', { tokens, emotion, style });
  },

  simplifyText: async (text, targetLevel = 'easy') => {
    return apiClient.post('/communication/simplify-text', { text, target_level: targetLevel });
  },

  synthesizeSpeech: async (text, voice = 'friendly_child', speed = 1.0) => {
    return apiClient.post('/communication/text-to-speech', { text, voice, speed });
  },

  checkinEmotion: async (emotion, intensity = 5, note = null) => {
    return apiClient.post('/communication/emotion-checkin', { emotion, intensity, note });
  },

  getSavedPhrases: async () => {
    return apiClient.get('/communication/saved-phrases');
  },

  savePhrase: async (text, tokens = [], category = 'Favorites', icon = '⭐') => {
    return apiClient.post('/communication/saved-phrases', { text, tokens, category, icon });
  },

  deleteSavedPhrase: async (phraseId) => {
    return apiClient.delete(`/communication/saved-phrases/${phraseId}`);
  },

  getHistory: async (limit = 30) => {
    return apiClient.get(`/communication/history?limit=${limit}`);
  },

  logCommunication: async (sentence, source = 'aac', emotion = null, audioPlayed = true) => {
    return apiClient.post('/communication/log', {
      sentence,
      source,
      emotion,
      audio_played: audioPlayed,
    });
  },
};

export default communicationApi;
