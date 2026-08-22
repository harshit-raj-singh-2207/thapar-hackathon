import { useEffect } from 'react';
import useLearningStore from '../store/learningStore';

export const useLearning = () => {
  const store = useLearningStore();

  useEffect(() => {
    if (store.routines.length === 0) {
      store.fetchRoutines();
      store.fetchTasks();
      store.fetchReminders();
      store.fetchTopics();
    }
  }, []);

  return {
    ...store,
  };
};

export default useLearning;
