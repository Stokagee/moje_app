import React from 'react';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import AppNavigator from './src/component/navigation/AppNavigator';
import { AppModalProvider } from './src/component/context/AppModalProvider';
// Import logger pro nastavení globálních error handlerů
import './src/utils/lokiLogger';

export default function App() {
  return (
    <SafeAreaProvider>
      <AppModalProvider>
        <AppNavigator />
      </AppModalProvider>
    </SafeAreaProvider>
  );
}