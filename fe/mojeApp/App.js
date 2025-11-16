import React from 'react';
import AppNavigator from './src/component/navigation/AppNavigator';
import { AppModalProvider } from './src/component/context/AppModalProvider';

export default function App() {
  return (
    <AppModalProvider>
      <AppNavigator />
    </AppModalProvider>
  );
}