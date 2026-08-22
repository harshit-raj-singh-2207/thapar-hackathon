import { useEffect } from 'react';
import useCommunicationStore from '../store/communicationStore';

export const useCommunication = () => {
  const store = useCommunicationStore();

  useEffect(() => {
    if (store.categories.length === 0) {
      store.fetchAACBoard();
      store.fetchSavedPhrases();
      store.fetchHistory();
    }
  }, []);

  return {
    ...store,
  };
};

export default useCommunication;
