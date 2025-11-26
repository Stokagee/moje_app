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
      {menuItems.map((item, index) => (
        <TouchableOpacity
          key={item.page}
          style={[
            styles.menuItem,
            currentPage === item.page && styles.menuItemActive,
          ]}
          onPress={() => handleNavigate(item.page)}
          // === TESTID - React Native standard ===
          testID={`menu-item-${item.page}`}
          // === NATIVEID - mapuje se na id ve webu ===
          nativeID={`menu-item-${item.page}`}
          // === ID - explicitní HTML id ===
          id={`nav-item-${item.page}`}
          // === NAME - název položky ===
          name={`menu-${item.page}`}
          // === DATA-* atributy pro CSS selektory ===
          data-testid={`menu-item-${item.page}`}
          data-component="menu-item"
          data-page={item.page}
          data-index={index}
          data-active={currentPage === item.page ? 'true' : 'false'}
          data-class={`menu-item nav-item ${currentPage === item.page ? 'menu-item-active' : ''}`}
          // === ACCESSIBILITY atributy ===
          accessibilityLabel={item.label}
          accessibilityRole="menuitem"
          accessibilityState={{ selected: currentPage === item.page }}
          accessibilityHint={`Navigovat na ${item.label}`}
          // === ARIA atributy (web) ===
          aria-label={item.label}
          aria-current={currentPage === item.page ? 'page' : undefined}
          // === CLASSNAME pro CSS selektory ===
          className={`menu-item nav-item ${currentPage === item.page ? 'menu-item-active' : ''}`}
        >
          <MaterialIcons
            name={item.icon}
            size={24}
            color={currentPage === item.page ? '#007AFF' : '#333'}
            // === ICON LOKÁTORY ===
            testID={`menu-item-${item.page}-icon`}
            nativeID={`menu-icon-${item.page}`}
            data-component="menu-icon"
            data-icon={item.icon}
            accessibilityLabel={`Ikona ${item.label}`}
          />
          <Text
            style={[
              styles.menuItemText,
              currentPage === item.page && styles.menuItemTextActive,
            ]}
            // === MENU ITEM TEXT LOKÁTORY ===
            testID={`menu-item-${item.page}-text`}
            nativeID={`menu-label-${item.page}`}
            id={`nav-label-${item.page}`}
            data-component="menu-label"
            data-page={item.page}
            data-class="menu-label nav-label"
            accessibilityRole="text"
            className="menu-label nav-label"
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
      <View
        style={styles.desktopContainer}
        // === DESKTOP CONTAINER LOKÁTORY ===
        testID="desktop-layout"
        nativeID="desktop-layout"
        id="layout-desktop"
        data-component="desktop-layout"
        data-layout="desktop"
        data-class="desktop-container layout-wrapper"
        className="desktop-container layout-wrapper"
      >
        {/* Sidebar */}
        <View
          style={styles.sidebar}
          // === SIDEBAR LOKÁTORY ===
          testID="desktop-sidebar"
          nativeID="desktop-sidebar"
          id="sidebar"
          name="sidebar"
          data-testid="desktop-sidebar"
          data-component="sidebar"
          data-layout="desktop"
          data-class="sidebar desktop-nav navigation"
          accessibilityRole="navigation"
          aria-label="Hlavní navigace"
          className="sidebar desktop-nav navigation"
        >
          {/* Logo/Nadpis */}
          <View
            style={styles.sidebarHeader}
            // === SIDEBAR HEADER LOKÁTORY ===
            testID="sidebar-header"
            nativeID="sidebar-header"
            id="nav-header"
            data-component="sidebar-header"
            data-class="sidebar-header nav-header"
            className="sidebar-header nav-header"
          >
            <MaterialIcons
              name="apps"
              size={32}
              color="#007AFF"
              testID="sidebar-logo-icon"
              nativeID="sidebar-logo"
              data-component="sidebar-logo"
              accessibilityLabel="Logo aplikace"
            />
            <Text
              style={styles.sidebarTitle}
              // === SIDEBAR TITLE LOKÁTORY ===
              testID="sidebar-title"
              nativeID="sidebar-title"
              id="nav-title"
              data-component="sidebar-title"
              data-class="sidebar-title nav-title"
              accessibilityRole="header"
              className="sidebar-title nav-title"
            >
              Menu
            </Text>
          </View>

          {/* Položky menu */}
          <View
            style={styles.sidebarMenu}
            // === SIDEBAR MENU LOKÁTORY ===
            testID="sidebar-menu"
            nativeID="sidebar-menu"
            id="nav-menu"
            data-component="sidebar-menu"
            data-class="sidebar-menu nav-list"
            accessibilityRole="menu"
            aria-label="Navigační menu"
            className="sidebar-menu nav-list"
          >
            {renderMenuItems()}
          </View>
        </View>

        {/* Obsah stránky */}
        <View
          style={styles.desktopContent}
          // === DESKTOP CONTENT LOKÁTORY ===
          testID="desktop-content"
          nativeID="desktop-content"
          id="main-content"
          data-component="page-content"
          data-class="desktop-content main-content"
          accessibilityRole="main"
          aria-label="Hlavní obsah"
          className="desktop-content main-content"
        >
          {children}
        </View>
      </View>
    );
  }

  // MOBILNÍ: Hamburger menu
  return (
    <View
      style={styles.mobileContainer}
      // === MOBILE CONTAINER LOKÁTORY ===
      testID="mobile-layout"
      nativeID="mobile-layout"
      id="layout-mobile"
      data-component="mobile-layout"
      data-layout="mobile"
      data-class="mobile-container layout-wrapper"
      className="mobile-container layout-wrapper"
    >
      {/* Hamburger tlačítko */}
      <TouchableOpacity
        style={styles.hamburgerButton}
        onPress={toggleMenu}
        // === HAMBURGER BUTTON LOKÁTORY ===
        testID="hamburger-button"
        nativeID="hamburger-button"
        id="hamburger-btn"
        name="hamburger"
        data-testid="hamburger-button"
        data-component="hamburger-button"
        data-action="toggle-menu"
        data-menu-open={isOpen ? 'true' : 'false'}
        data-class="btn hamburger-btn toggle-menu"
        accessibilityLabel="Otevřít menu"
        accessibilityRole="button"
        accessibilityState={{ expanded: isOpen }}
        accessibilityHint="Klikněte pro otevření navigačního menu"
        aria-label="Otevřít menu"
        aria-expanded={isOpen}
        aria-controls="mobile-menu"
        className="btn hamburger-btn toggle-menu"
      >
        <MaterialIcons
          name="menu"
          size={28}
          color="#333"
          testID="hamburger-icon"
          nativeID="hamburger-icon"
          data-component="hamburger-icon"
          accessibilityLabel="Menu ikona"
        />
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
        <View
          style={styles.modalContainer}
          // === MODAL CONTAINER LOKÁTORY ===
          testID="mobile-menu-modal"
          nativeID="mobile-menu-container"
          id="mobile-menu"
          data-component="mobile-menu-modal"
          data-class="modal-container menu-modal"
          className="modal-container menu-modal"
        >
          {/* Overlay pro zavření menu */}
          <TouchableOpacity
            style={styles.overlay}
            activeOpacity={1}
            onPress={toggleMenu}
            // === OVERLAY LOKÁTORY ===
            testID="menu-overlay"
            nativeID="menu-overlay"
            id="menu-backdrop"
            data-testid="menu-overlay"
            data-component="menu-overlay"
            data-action="close-menu"
            data-class="overlay menu-overlay backdrop"
            accessibilityLabel="Zavřít menu"
            accessibilityRole="none"
            aria-label="Klikněte pro zavření menu"
            className="overlay menu-overlay backdrop"
          />

          {/* Menu panel */}
          <View
            style={styles.menuPanel}
            // === MENU PANEL LOKÁTORY ===
            testID="hamburger-menu-panel"
            nativeID="hamburger-menu-panel"
            id="side-menu"
            name="mobile-nav"
            data-testid="hamburger-menu-panel"
            data-component="menu-panel"
            data-layout="mobile"
            data-class="menu-panel side-menu mobile-nav"
            accessibilityRole="menu"
            aria-label="Navigační menu"
            className="menu-panel side-menu mobile-nav"
          >
            {/* Zavírací tlačítko */}
            <TouchableOpacity
              style={styles.closeButton}
              onPress={toggleMenu}
              // === CLOSE BUTTON LOKÁTORY ===
              testID="menu-close-button"
              nativeID="menu-close-button"
              id="close-menu-btn"
              name="close-menu"
              data-testid="menu-close-button"
              data-component="close-button"
              data-action="close-menu"
              data-class="btn btn-close close-menu"
              accessibilityLabel="Zavřít menu"
              accessibilityRole="button"
              accessibilityHint="Klikněte pro zavření menu"
              aria-label="Zavřít menu"
              className="btn btn-close close-menu"
            >
              <MaterialIcons
                name="close"
                size={28}
                color="#333"
                testID="close-menu-icon"
                nativeID="close-icon"
                data-component="close-icon"
                accessibilityLabel="Zavřít"
              />
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
