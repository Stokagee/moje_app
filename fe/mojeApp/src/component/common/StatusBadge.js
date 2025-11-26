/**
 * StatusBadge - Univerzalni badge pro zobrazeni statusu
 * Food Delivery System - Phase 1
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

/**
 * Univerzalni badge pro zobrazeni statusu
 *
 * @param {string} status - Hodnota statusu (klic v statusConfig)
 * @param {object} statusConfig - Konfigurace barev a labelu
 * @param {string} size - 'small' | 'medium' | 'large'
 * @param {string} testID - Test ID pro automatizaci
 */
const StatusBadge = ({ status, statusConfig, size = 'medium', testID }) => {
  // Fallback konfigurace pokud status neni v configu
  const config = statusConfig?.[status] || {
    label: status,
    color: '#6c757d',
    backgroundColor: '#f8f9fa',
  };

  // Velikostni varianty
  const sizeStyles = {
    small: { paddingHorizontal: 6, paddingVertical: 2, fontSize: 10 },
    medium: { paddingHorizontal: 10, paddingVertical: 4, fontSize: 12 },
    large: { paddingHorizontal: 14, paddingVertical: 6, fontSize: 14 },
  };

  const currentSize = sizeStyles[size] || sizeStyles.medium;

  return (
    <View
      style={[
        styles.badge,
        {
          backgroundColor: config.backgroundColor,
          paddingHorizontal: currentSize.paddingHorizontal,
          paddingVertical: currentSize.paddingVertical,
        },
      ]}
      // === TESTID - React Native standard ===
      testID={testID}
      // === NATIVEID - mapuje se na id ve webu ===
      nativeID={testID || `status-badge-${status}`}
      // === ID - explicitní HTML id ===
      id={`badge-${status}`}
      // === NAME - název badge ===
      name={`status-${status}`}
      // === DATA-* atributy pro CSS selektory ===
      data-testid={testID}
      data-component="status-badge"
      data-status={status}
      data-size={size}
      data-label={config.label}
      data-class={`status-badge badge-${status} badge-${size}`}
      // === ACCESSIBILITY atributy ===
      accessibilityLabel={`Status: ${config.label}`}
      accessibilityRole="text"
      accessibilityHint={`Aktuální stav: ${config.label}`}
      // === ARIA atributy (web) ===
      aria-label={`Status: ${config.label}`}
      // === CLASSNAME pro CSS selektory ===
      className={`status-badge badge-${status} badge-${size}`}
    >
      <Text
        style={[
          styles.text,
          {
            color: config.color,
            fontSize: currentSize.fontSize,
          },
        ]}
        // === BADGE TEXT LOKÁTORY ===
        testID={testID ? `${testID}-text` : `status-badge-${status}-text`}
        nativeID={`status-text-${status}`}
        id={`status-label-${status}`}
        data-component="badge-text"
        data-status={status}
        data-class="badge-text status-label"
        accessibilityRole="text"
        className="badge-text status-label"
      >
        {config.label}
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  // Kontejner badge - pill tvar
  badge: {
    borderRadius: 12,
    alignSelf: 'flex-start',
  },
  // Text uvnitr badge
  text: {
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
});

export default StatusBadge;
