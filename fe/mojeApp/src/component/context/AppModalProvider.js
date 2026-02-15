import React, { createContext, useCallback, useContext, useState } from 'react';
import AppModal from '../common/AppModal';

export const AppModalContext = createContext(null);

export const AppModalProvider = ({ children }) => {
  const [modalProps, setModalProps] = useState({ visible: false });

  const showModal = useCallback((props = {}) => {
    setModalProps({ visible: true, ...props });
  }, []);

  const hideModal = useCallback(() => {
    setModalProps({ visible: false });
  }, []);

  return (
    <AppModalContext.Provider value={{ showModal, hideModal }}>
      {children}
      <AppModal
        visible={!!modalProps.visible}
        title={modalProps.title}
        message={modalProps.message}
        primaryText={modalProps.primaryText || 'OK'}
        secondaryText={modalProps.secondaryText}
        onClose={hideModal}
        onPrimary={() => {
          if (modalProps.onPrimary) modalProps.onPrimary();
          hideModal();
        }}
        onSecondary={() => {
          if (modalProps.onSecondary) modalProps.onSecondary();
          hideModal();
        }}
        testID={modalProps.testID || 'appModal'}
      />
    </AppModalContext.Provider>
  );
};

export const useAppModalContext = () => useContext(AppModalContext);

export default AppModalProvider;
