/**
 * LoadingScreen - Loading indikator s volitelnym overlay
 * Food Delivery System - Phase 1
 */

import React from 'react';
import {
  View,
  Text,
  ActivityIndicator,
  StyleSheet,
  Modal,
} from 'react-native';

/**
 * Loading indikator s volitelnym overlay
 *
 * @param {boolean} visible - Zobrazit loading
 * @param {string} message - Volitelna zprava pod spinnerem
 * @param {boolean} overlay - Zobrazit jako overlay pres cely screen
 * @param {string} size - 'small' | 'large'
 * @param {string} testID - Test ID pro automatizaci
 */
const LoadingScreen = ({
  visible = true,
  message,
  overlay = false,
  size = 'large',
  testID = 'loading-screen',
}) => {
  if (!visible) {
    return null;
  }

  const content = (
    <View
      style={[styles.container, overlay && styles.overlayContainer]}
      // === TESTID - React Native standard ===
      testID={testID}
      // === NATIVEID - mapuje se na id ve webu ===
      nativeID={testID}
      // === ID - explicitní HTML id ===
      id="loading-container"
      // === NAME - název komponenty ===
      name="loading"
      // === DATA-* atributy pro CSS selektory ===
      data-testid={testID}
      data-component="loading-screen"
      data-loading="true"
      data-overlay={overlay ? 'true' : 'false'}
      data-size={size}
      data-class={`loading-screen ${overlay ? 'loading-overlay' : ''}`}
      // === ACCESSIBILITY atributy ===
      accessibilityLabel={message || 'Načítání'}
      accessibilityRole="progressbar"
      accessibilityHint="Prosím čekejte"
      // === ARIA atributy (web) ===
      aria-label={message || 'Načítání'}
      aria-busy="true"
      aria-live="polite"
      // === CLASSNAME pro CSS selektory ===
      className={`loading-screen ${overlay ? 'loading-overlay' : ''}`}
    >
      <View
        style={styles.spinnerBox}
        // === SPINNER BOX LOKÁTORY ===
        testID={`${testID}-box`}
        nativeID="spinner-box"
        id="loading-box"
        data-component="spinner-container"
        data-class="spinner-box loading-box"
        accessibilityRole="none"
        className="spinner-box loading-box"
      >
        <ActivityIndicator
          size={size}
          color="#007AFF"
          // === SPINNER LOKÁTORY ===
          testID={`${testID}-spinner`}
          nativeID="loading-spinner"
          id="spinner"
          data-component="spinner"
          data-size={size}
          data-class="spinner activity-indicator"
          accessibilityLabel="Načítání"
        />
        {message && (
          <Text
            style={styles.message}
            // === MESSAGE LOKÁTORY ===
            testID={`${testID}-message`}
            nativeID="loading-message"
            id="loading-text"
            data-component="loading-message"
            data-class="loading-text message"
            accessibilityRole="text"
            aria-live="polite"
            className="loading-text message"
          >
            {message}
          </Text>
        )}
      </View>
    </View>
  );

  // Overlay mod = zobraz jako modal
  if (overlay) {
    return (
      <Modal
        visible={visible}
        transparent
        animationType="fade"
        testID={`${testID}-modal`}
      >
        {content}
      </Modal>
    );
  }

  return content;
};

const styles = StyleSheet.create({
  // Zakladni kontejner
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  // Overlay kontejner s polopruhlednym pozadim
  overlayContainer: {
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
  },
  // Box kolem spinneru
  spinnerBox: {
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#fff',
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
  },
  // Zprava pod spinnerem
  message: {
    marginTop: 12,
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
  },
});

export default LoadingScreen;
