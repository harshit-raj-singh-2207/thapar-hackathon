import { create } from 'zustand';
import communicationApi from '../services/api/communicationApi';
import { Platform } from 'react-native';

export const useCommunicationStore = create((set, get) => ({
  categories: [],
  selectedCategory: 'Quick Needs',
  sentenceTokens: [],
  generatedSentence: '',
  suggestedAlternatives: [],
  savedPhrases: [],
  historyLogs: [],
  currentEmotion: null,
  emotionIntensity: 5,
  emotionRecommendations: [],
  sensoryTip: null,
  loading: false,
  speaking: false,
  error: null,

  // Fetch AAC board categories & cards
  fetchAACBoard: async () => {
    set({ loading: true, error: null });
    try {
      const data = await communicationApi.getAACBoard();
      if (Array.isArray(data) && data.length > 0) {
        set({ categories: data, selectedCategory: data[0].name });
      }
    } catch (err) {
      console.warn('Using fallback AAC categories:', err);
      // Client-side fallback board ensuring zero empty states
      const fallback = [
        {
          id: 'cat-quick',
          name: 'Quick Needs',
          icon: '⭐',
          color: '#2563EB',
          cards: [
            { id: 'c-water', label: 'Water', icon: '💧', spoken_text: 'water' },
            { id: 'c-food', label: 'Food', icon: '🍴', spoken_text: 'food' },
            { id: 'c-toilet', label: 'Toilet', icon: '🚻', spoken_text: 'toilet' },
            { id: 'c-help', label: 'Help', icon: '🛟', spoken_text: 'help' },
            { id: 'c-sleep', label: 'Sleep', icon: '🛏️', spoken_text: 'sleep' },
            { id: 'c-play', label: 'Play', icon: '🚗', spoken_text: 'play' },
          ],
        },
        {
          id: 'cat-food',
          name: 'Food',
          icon: '🍴',
          color: '#F59E0B',
          cards: [
            { id: 'c-apple', label: 'Apple', icon: '🍎' },
            { id: 'c-bread', label: 'Bread', icon: '🍞' },
            { id: 'c-snack', label: 'Snack', icon: '🍪' },
            { id: 'c-fruit', label: 'Fruit', icon: '🍓' },
          ],
        },
        {
          id: 'cat-drink',
          name: 'Drink',
          icon: '🥤',
          color: '#3B82F6',
          cards: [
            { id: 'c-water2', label: 'Water', icon: '💧' },
            { id: 'c-juice', label: 'Juice', icon: '🧃' },
            { id: 'c-milk', label: 'Milk', icon: '🥛' },
            { id: 'c-smoothie', label: 'Smoothie', icon: '🥤' },
          ],
        },
        {
          id: 'cat-actions',
          name: 'Actions',
          icon: '🏃',
          color: '#10B981',
          cards: [
            { id: 'c-i', label: 'I', icon: '👤' },
            { id: 'c-want', label: 'WANT', icon: '👋' },
            { id: 'c-need', label: 'NEED', icon: '✋' },
            { id: 'c-feel', label: 'FEEL', icon: '❤️' },
            { id: 'c-stop', label: 'STOP', icon: '🛑' },
            { id: 'c-yes', label: 'YES', icon: '✅' },
            { id: 'c-no', label: 'NO', icon: '❌' },
          ],
        },
      ];
      set({ categories: fallback, selectedCategory: 'Quick Needs' });
    } finally {
      set({ loading: false });
    }
  },

  setSelectedCategory: (catName) => {
    set({ selectedCategory: catName });
  },

  // Token sentence strip manipulation
  addToken: (card) => {
    const tokens = [...get().sentenceTokens, card];
    set({ sentenceTokens: tokens });
    get().buildSentenceFromTokens(tokens);
  },

  removeToken: (index) => {
    const tokens = get().sentenceTokens.filter((_, i) => i !== index);
    set({ sentenceTokens: tokens });
    if (tokens.length > 0) {
      get().buildSentenceFromTokens(tokens);
    } else {
      set({ generatedSentence: '', suggestedAlternatives: [] });
    }
  },

  clearTokens: () => {
    set({ sentenceTokens: [], generatedSentence: '', suggestedAlternatives: [] });
  },

  buildSentenceFromTokens: async (tokens) => {
    if (!tokens || tokens.length === 0) return;
    try {
      const labels = tokens.map((t) => (typeof t === 'string' ? t : t.label));
      const res = await communicationApi.buildSentence(labels, get().currentEmotion);
      if (res && res.generated_sentence) {
        set({
          generatedSentence: res.generated_sentence,
          suggestedAlternatives: res.suggested_alternatives || [],
        });
      }
    } catch (e) {
      const simple = tokens.map((t) => (typeof t === 'string' ? t : t.label)).join(' ');
      set({ generatedSentence: `I want ${simple.toLowerCase()}, please.` });
    }
  },

  // Speak text via browser Web Speech API or client TTS
  speakSentence: async (textToSpeak) => {
    const text = textToSpeak || get().generatedSentence || get().sentenceTokens.map((t) => t.label).join(' ');
    if (!text) return;

    set({ speaking: true });

    // Client-side Web Speech Synthesis for high reliability on web/expo
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.95; // slightly slower for clear neurodivergent listening
      utterance.pitch = 1.1; // friendly tone
      utterance.onend = () => set({ speaking: false });
      utterance.onerror = () => set({ speaking: false });
      window.speechSynthesis.speak(utterance);
    } else {
      setTimeout(() => set({ speaking: false }), 2000);
    }

    // Log to backend
    try {
      await communicationApi.logCommunication(text, 'aac', get().currentEmotion, true);
      get().fetchHistory();
    } catch (e) {
      // Ignore network log error
    }
  },

  // Save current phrase
  saveCurrentPhrase: async () => {
    const text = get().generatedSentence || get().sentenceTokens.map((t) => t.label).join(' ');
    if (!text) return;

    try {
      await communicationApi.savePhrase(text, get().sentenceTokens.map((t) => t.label));
      get().fetchSavedPhrases();
    } catch (e) {
      console.warn('Save phrase failed:', e);
    }
  },

  fetchSavedPhrases: async () => {
    try {
      const data = await communicationApi.getSavedPhrases();
      if (Array.isArray(data)) set({ savedPhrases: data });
    } catch (e) {
      console.warn('Fetch saved phrases fallback:', e);
    }
  },

  fetchHistory: async () => {
    try {
      const data = await communicationApi.getHistory(20);
      if (Array.isArray(data)) set({ historyLogs: data });
    } catch (e) {
      console.warn('Fetch history fallback:', e);
    }
  },

  // Emotion check-in
  checkinEmotion: async (emotion, intensity = 5) => {
    set({ currentEmotion: emotion, emotionIntensity: intensity });
    try {
      const res = await communicationApi.checkinEmotion(emotion, intensity);
      if (res) {
        set({
          emotionRecommendations: res.recommended_phrases || [],
          sensoryTip: res.sensory_tip || null,
        });
      }
    } catch (e) {
      console.warn('Emotion checkin fallback:', e);
    }
  },
}));

export default useCommunicationStore;
