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
      testID={testID}
      nativeID={testID}
      accessibilityLabel={message || 'Nacitani'}
      accessibilityRole="progressbar"
      data-class="loading-screen"
      data-loading="true"
    >
      <View style={styles.spinnerBox}>
        <ActivityIndicator
          size={size}
          color="#007AFF"
          testID={`${testID}-spinner`}
        />
        {message && (
          <Text style={styles.message} testID={`${testID}-message`}>
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
