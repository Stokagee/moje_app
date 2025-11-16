import { registerRootComponent } from 'expo';
import { Platform } from 'react-native';
import App from './App';

// Pro web použij ReactDOM místo Expo registerRootComponent
if (Platform.OS === 'web') {
  const ReactDOM = require('react-dom/client');
  const root = ReactDOM.createRoot(document.getElementById('root'));
  root.render(<App />);
} else {
  // Pro mobil použij Expo
  registerRootComponent(App);
}
