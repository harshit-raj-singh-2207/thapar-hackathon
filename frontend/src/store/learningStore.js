import { create } from 'zustand';
import learningApi from '../services/api/learningApi';

export const useLearningStore = create((set, get) => ({
  routines: [],
  activeRoutine: null,
  tasks: [],
  activeTask: null,
  brokenDownSteps: [],
  reminders: [],
  topics: [],
  activeTopic: null,
  tutorMessages: [
    {
      id: 'welcome-tutor',
      sender: 'tutor',
      text: "Hi there! I'm Nivi, your friendly AI learning buddy. 🌟 Ask me anything or choose a topic to explore together!",
      simple_analogy: 'We can discover amazing things step by step!',
      follow_up_questions: ['Why is the sky blue?', 'How do dinosaurs eat?', 'What does a friend do?'],
      icon: '🤖',
    },
  ],
  loading: false,
  tutorLoading: false,
  error: null,

  fetchRoutines: async () => {
    set({ loading: true, error: null });
    try {
      const data = await learningApi.getRoutines();
      if (Array.isArray(data)) set({ routines: data });
    } catch (err) {
      console.warn('Fallback routines:', err);
      set({
        routines: [
          {
            id: 'routine-morning-1',
            title: 'Morning Sunshine Routine',
            time_of_day: 'morning',
            icon: '🌅',
            color: '#3B82F6',
            streak_days: 4,
            steps: [
              { id: 's1', step_number: 1, title: 'Wake up & stretch', instruction: 'Gentle stretches and open curtains.', icon: '🧘', duration_sec: 60, is_completed: true },
              { id: 's2', step_number: 2, title: 'Brush teeth', instruction: 'Scrub circles on top and bottom.', icon: '🪥', duration_sec: 120, is_completed: true },
              { id: 's3', step_number: 3, title: 'Wash face & hands', instruction: 'Warm water and dry with soft towel.', icon: '🧼', duration_sec: 60, is_completed: false },
              { id: 's4', step_number: 4, title: 'Put on clothes', instruction: 'Shirt, pants, and cozy socks.', icon: '👕', duration_sec: 180, is_completed: false },
              { id: 's5', step_number: 5, title: 'Healthy breakfast', instruction: 'Eat breakfast and drink water.', icon: '🥣', duration_sec: 600, is_completed: false },
            ],
          },
          {
            id: 'routine-bedtime-1',
            title: 'Calm Bedtime Wind-Down',
            time_of_day: 'bedtime',
            icon: '🌙',
            color: '#8B5CF6',
            streak_days: 6,
            steps: [
              { id: 'b1', step_number: 1, title: 'Put on pajamas', instruction: 'Cozy nightwear.', icon: '🧸', duration_sec: 120, is_completed: false },
              { id: 'b2', step_number: 2, title: 'Night tooth brushing', instruction: '2 minutes clean teeth.', icon: '🪥', duration_sec: 120, is_completed: false },
              { id: 'b3', step_number: 3, title: 'Bedtime story', instruction: 'Read 1 story in dim light.', icon: '📖', duration_sec: 300, is_completed: false },
              { id: 'b4', step_number: 4, title: 'Lights off & rest', instruction: 'Cozy blanket and sweet dreams.', icon: '🌌', duration_sec: 60, is_completed: false },
            ],
          },
        ],
      });
    } finally {
      set({ loading: false });
    }
  },

  toggleStep: async (routineId, stepId) => {
    const routines = get().routines.map((r) => {
      if (r.id === routineId) {
        const steps = (r.steps || []).map((s) => (s.id === stepId ? { ...s, is_completed: !s.is_completed } : s));
        const allDone = steps.every((s) => s.is_completed);
        return {
          ...r,
          steps,
          streak_days: allDone ? (r.streak_days || 0) + 1 : r.streak_days,
        };
      }
      return r;
    });
    set({ routines });

    try {
      await learningApi.toggleRoutineStep(stepId);
    } catch (e) {
      // Offline fallback maintained
    }
  },

  resetRoutine: async (routineId) => {
    const routines = get().routines.map((r) => {
      if (r.id === routineId) {
        const steps = (r.steps || []).map((s) => ({ ...s, is_completed: false }));
        return { ...r, steps };
      }
      return r;
    });
    set({ routines });

    try {
      await learningApi.resetRoutine(routineId);
    } catch (e) {
      // Offline fallback maintained
    }
  },

  // AI Task Breakdown
  breakdownTask: async (taskTitle) => {
    set({ loading: true, error: null });
    try {
      const res = await learningApi.breakdownTaskAI(taskTitle);
      if (res && res.steps) {
        set({ brokenDownSteps: res.steps });
      }
    } catch (err) {
      console.warn('Fallback task breakdown:', err);
      set({
        brokenDownSteps: [
          { step_number: 1, title: 'Get materials ready', instruction: `Prepare items needed for ${taskTitle}.`, icon: '🏁', duration_sec: 30 },
          { step_number: 2, title: 'Start first action', instruction: 'Take your time and do step 1 calmly.', icon: '1️⃣', duration_sec: 60 },
          { step_number: 3, title: 'Complete main action', instruction: 'Keep up the great momentum!', icon: '⭐', duration_sec: 90 },
          { step_number: 4, title: 'Check and finish', instruction: 'Inspect your work and put items away.', icon: '✅', duration_sec: 30 },
        ],
      });
    } finally {
      set({ loading: false });
    }
  },

  fetchTasks: async () => {
    try {
      const data = await learningApi.getTasks();
      if (Array.isArray(data)) set({ tasks: data });
    } catch (e) {
      console.warn('Tasks fallback:', e);
    }
  },

  fetchReminders: async () => {
    try {
      const data = await learningApi.getReminders();
      if (Array.isArray(data)) set({ reminders: data });
    } catch (e) {
      console.warn('Reminders fallback:', e);
      set({
        reminders: [
          { id: 'rem-water-1', title: 'Drink Water (Hydration Break)', time_str: '10:00 AM', frequency: 'Daily', category: 'Hydration', icon: '💧', is_active: true },
          { id: 'rem-sensory-1', title: '5-Minute Sensory Calming Break', time_str: '02:30 PM', frequency: 'Weekdays', category: 'Sensory Break', icon: '🎧', is_active: true },
          { id: 'rem-homework-1', title: 'Visual Learning & Puzzle Time', time_str: '04:30 PM', frequency: 'Weekdays', category: 'Routine', icon: '🧩', is_active: true },
        ],
      });
    }
  },

  toggleReminder: async (reminderId) => {
    const rems = get().reminders.map((r) => (r.id === reminderId ? { ...r, is_active: !r.is_active } : r));
    set({ reminders: rems });

    try {
      await learningApi.toggleReminder(reminderId);
    } catch (e) {
      // Handled in store
    }
  },

  // AI Tutor Ask
  askTutor: async (question) => {
    if (!question.trim()) return;

    const userMsg = {
      id: `user-${Date.now()}`,
      sender: 'child',
      text: question,
      timestamp: new Date().toLocaleTimeString(),
    };

    set((state) => ({
      tutorMessages: [...state.tutorMessages, userMsg],
      tutorLoading: true,
    }));

    try {
      const res = await learningApi.askTutor(question);
      const tutorReply = {
        id: `tutor-${Date.now()}`,
        sender: 'tutor',
        text: res.reply,
        simple_analogy: res.simple_analogy,
        follow_up_questions: res.follow_up_questions || [],
        icon: res.icon || '💡',
        timestamp: new Date().toLocaleTimeString(),
      };
      set((state) => ({
        tutorMessages: [...state.tutorMessages, tutorReply],
      }));
    } catch (e) {
      const fallbackReply = {
        id: `tutor-${Date.now()}`,
        sender: 'tutor',
        text: `✨ Learning about "${question}" is super fun! Let's take it one step at a time!`,
        simple_analogy: 'Curiosity is like a superhero muscle that gets stronger every day!',
        follow_up_questions: ['Tell me more!', 'Can we do a fun quiz?'],
        icon: '🌟',
      };
      set((state) => ({
        tutorMessages: [...state.tutorMessages, fallbackReply],
      }));
    } finally {
      set({ tutorLoading: false });
    }
  },

  fetchTopics: async () => {
    try {
      const data = await learningApi.getTopics();
      if (Array.isArray(data)) set({ topics: data });
    } catch (e) {
      console.warn('Topics fallback:', e);
      set({
        topics: [
          {
            id: 'topic-social-1',
            title: 'Taking Turns on the Playground',
            category: 'Social Stories',
            description: 'Learn how to share swings and ask friends to play together politely.',
            icon: '🛝',
            color: '#10B981',
            progress_pct: 60,
          },
          {
            id: 'topic-emotion-1',
            title: 'When Noises Get Too Loud',
            category: 'Emotion Regulation',
            description: 'Steps to handle loud sirens, blenders, or crowded rooms peacefully.',
            icon: '🎧',
            color: '#3B82F6',
            progress_pct: 85,
          },
          {
            id: 'topic-skills-1',
            title: 'Tying Shoes Step-by-Step',
            category: 'Daily Life Skills',
            description: 'Bunny ears method made simple with visual colors.',
            icon: '👟',
            color: '#F59E0B',
            progress_pct: 40,
          },
          {
            id: 'topic-science-1',
            title: 'Secrets of the Solar System',
            category: 'Science & Nature',
            description: 'Meet the 8 planets and their moons with fun analogies.',
            icon: '🪐',
            color: '#8B5CF6',
            progress_pct: 100,
            is_completed: true,
          },
        ],
      });
    }
  },
}));

export default useLearningStore;
