import { useContext } from 'react';
import { AppModalContext } from './AppModalProvider';

const useAppModal = () => {
  const ctx = useContext(AppModalContext);
  if (!ctx) {
    throw new Error('useAppModal must be used within AppModalProvider');
  }
  return ctx;
};

export default useAppModal;
