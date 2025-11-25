import React, { useState } from 'react';
import { View, StyleSheet } from 'react-native';
import FormPage from '../pages/FormPage';
import Page2 from '../pages/Page2';
import Page3 from '../pages/Page3';
import Page4 from '../pages/Page4';
import NavigationMenu from '../common/HamburgerMenu';

// Jednoduchá navigace pro web kompatibilitu
export default function AppNavigator() {
  const [currentPage, setCurrentPage] = useState('FormPage');

  const navigate = (pageName) => {
    setCurrentPage(pageName);
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'FormPage':
        return <FormPage navigation={{ navigate }} />;
      case 'Page2':
        return <Page2 navigation={{ navigate }} />;
      case 'Page3':
        return <Page3 navigation={{ navigate }} />;
      case 'Page4':
        return <Page4 navigation={{ navigate }} />;
      default:
        return <FormPage navigation={{ navigate }} />;
    }
  };

  return (
    <View style={styles.container}>
      <NavigationMenu
        currentPage={currentPage}
        onNavigate={navigate}
      >
        {renderPage()}
      </NavigationMenu>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});