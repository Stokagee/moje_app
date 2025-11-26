import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  Modal,
  StyleSheet,
  useWindowDimensions,
} from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';

/**
 * Navigační menu komponenta.
 * - Mobilní rozlišení (< 768px): Hamburger menu
 * - Desktop rozlišení (>= 768px): Permanentní levý sidebar
 *
 * @param {string} currentPage - Aktuálně zobrazená stránka
 * @param {function} onNavigate - Funkce pro navigaci na jinou stránku
 * @param {React.ReactNode} children - Obsah stránky (pouze pro desktop layout)
 */
const NavigationMenu = ({ currentPage, onNavigate, children }) => {
  const [isOpen, setIsOpen] = useState(false);
  const { width } = useWindowDimensions();

  const isMobile = width < 768;

  // Definice položek menu
  const menuItems = [
    { page: 'FormPage', label: 'Formulář', icon: 'edit' },
    { page: 'Page2', label: 'Seznam', icon: 'list' },
    { page: 'Page3', label: 'Objednavky', icon: 'receipt' },
    { page: 'Page4', label: 'Dispatch', icon: 'local-shipping' },
  ];

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const handleNavigate = (page) => {
    onNavigate(page);
    setIsOpen(false);
  };

  // Renderování položek menu (společné pro mobil i desktop)
  const renderMenuItems = () => (
    <>
      {menuItems.map((item) => (
        <TouchableOpacity
          key={item.page}
          style={[
            styles.menuItem,
            currentPage === item.page && styles.menuItemActive,
          ]}
          onPress={() => handleNavigate(item.page)}
          testID={`menu-item-${item.page}`}
          // Lokátory pro RF demonstraci
          nativeID={`menu-item-${item.page}`}
          accessibilityLabel={item.label}
          accessibilityRole="menuitem"
          data-class="menu-item"
          data-page={item.page}
        >
          <MaterialIcons
            name={item.icon}
            size={24}
            color={currentPage === item.page ? '#007AFF' : '#333'}
          />
          <Text
            style={[
              styles.menuItemText,
              currentPage === item.page && styles.menuItemTextActive,
            ]}
          >
            {item.label}
          </Text>
        </TouchableOpacity>
      ))}
    </>
  );

  // DESKTOP: Permanentní sidebar
  if (!isMobile) {
    return (
      <View style={styles.desktopContainer}>
        {/* Sidebar */}
        <View
          style={styles.sidebar}
          testID="desktop-sidebar"
          nativeID="desktop-sidebar"
          accessibilityRole="navigation"
          data-class="sidebar desktop-nav"
        >
          {/* Logo/Nadpis */}
          <View style={styles.sidebarHeader}>
            <MaterialIcons name="apps" size={32} color="#007AFF" />
            <Text
              style={styles.sidebarTitle}
              testID="sidebar-title"
              nativeID="sidebar-title"
              data-class="sidebar-title"
            >
              Menu
            </Text>
          </View>

          {/* Položky menu */}
          <View
            style={styles.sidebarMenu}
            testID="sidebar-menu"
            nativeID="sidebar-menu"
            accessibilityRole="menu"
            data-class="sidebar-menu"
          >
            {renderMenuItems()}
          </View>
        </View>

        {/* Obsah stránky */}
        <View style={styles.desktopContent}>
          {children}
        </View>
      </View>
    );
  }

  // MOBILNÍ: Hamburger menu
  return (
    <View style={styles.mobileContainer}>
      {/* Hamburger tlačítko */}
      <TouchableOpacity
        style={styles.hamburgerButton}
        onPress={toggleMenu}
        testID="hamburger-button"
        nativeID="hamburger-button"
        accessibilityLabel="Otevřít menu"
        accessibilityRole="button"
        data-class="btn hamburger-btn"
        data-action="toggle-menu"
      >
        <MaterialIcons name="menu" size={28} color="#333" />
      </TouchableOpacity>

      {/* Obsah stránky */}
      {children}

      {/* Modální menu */}
      <Modal
        visible={isOpen}
        transparent
        animationType="fade"
        onRequestClose={toggleMenu}
      >
        <View style={styles.modalContainer}>
          {/* Overlay pro zavření menu */}
          <TouchableOpacity
            style={styles.overlay}
            activeOpacity={1}
            onPress={toggleMenu}
            testID="menu-overlay"
            nativeID="menu-overlay"
            accessibilityLabel="Zavřít menu"
            data-class="overlay menu-overlay"
          />

          {/* Menu panel */}
          <View
            style={styles.menuPanel}
            testID="hamburger-menu-panel"
            nativeID="hamburger-menu-panel"
            accessibilityRole="menu"
            data-class="menu-panel side-menu"
          >
            {/* Zavírací tlačítko */}
            <TouchableOpacity
              style={styles.closeButton}
              onPress={toggleMenu}
              testID="menu-close-button"
              nativeID="menu-close-button"
              accessibilityLabel="Zavřít menu"
              accessibilityRole="button"
              data-class="btn close-btn"
              data-action="close-menu"
            >
              <MaterialIcons name="close" size={28} color="#333" />
            </TouchableOpacity>

            {/* Položky menu */}
            {renderMenuItems()}
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  // === DESKTOP STYLY ===
  desktopContainer: {
    flex: 1,
    flexDirection: 'row',
  },
  sidebar: {
    width: 220,
    backgroundColor: '#f8f9fa',
    borderRightWidth: 1,
    borderRightColor: '#e9ecef',
    paddingTop: 20,
  },
  sidebarHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingBottom: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
    marginBottom: 10,
  },
  sidebarTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginLeft: 10,
    color: '#333',
  },
  sidebarMenu: {
    flex: 1,
  },
  desktopContent: {
    flex: 1,
  },

  // === MOBILNÍ STYLY ===
  mobileContainer: {
    flex: 1,
  },
  hamburgerButton: {
    alignSelf: 'flex-start',
    marginLeft: 16,
    marginTop: 10,
    marginBottom: 5,
    padding: 10,
    backgroundColor: '#fff',
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  modalContainer: {
    flex: 1,
    flexDirection: 'row-reverse',
  },
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  menuPanel: {
    width: 250,
    backgroundColor: '#fff',
    paddingTop: 60,
    shadowColor: '#000',
    shadowOffset: { width: 2, height: 0 },
    shadowOpacity: 0.25,
    shadowRadius: 10,
    elevation: 5,
  },
  closeButton: {
    position: 'absolute',
    top: 10,
    left: 10,
    padding: 10,
  },

  // === SPOLEČNÉ STYLY ===
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 15,
    paddingHorizontal: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  menuItemActive: {
    backgroundColor: '#e8f4ff',
    borderRightWidth: 3,
    borderRightColor: '#007AFF',
  },
  menuItemText: {
    fontSize: 16,
    marginLeft: 15,
    color: '#333',
  },
  menuItemTextActive: {
    color: '#007AFF',
    fontWeight: 'bold',
  },
});

export default NavigationMenu;
