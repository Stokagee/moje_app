/**
 * PriorityBadge - VIP/priority indikator
 * Food Delivery System - Phase 1
 *
 * Zobrazuje se pouze pro VIP/high priority objednavky
 * Normalni priorita = nic se nezobrazuje
 */

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';

/**
 * Badge pro zobrazeni priority (VIP)
 *
 * @param {string} priority - 'normal' | 'high'
 * @param {boolean} isVip - Alternativne primo VIP flag z backendu
 * @param {string} testID - Test ID pro automatizaci
 */
const PriorityBadge = ({ priority, isVip, testID }) => {
  // Normalni priorita = nic nezobrazujeme
  const showBadge = priority === 'high' || isVip === true;

  if (!showBadge) {
    return null;
  }

  return (
    <View
      style={styles.badge}
      // === TESTID - React Native standard ===
      testID={testID}
      // === NATIVEID - mapuje se na id ve webu ===
      nativeID={testID || 'priority-badge-vip'}
      // === ID - explicitní HTML id ===
      id="priority-vip"
      // === NAME - název badge ===
      name="priority-high"
      // === DATA-* atributy pro CSS selektory ===
      data-testid={testID}
      data-component="priority-badge"
      data-priority="high"
      data-vip="true"
      data-class="priority-badge vip-badge"
      // === ACCESSIBILITY atributy ===
      accessibilityLabel="VIP objednávka"
      accessibilityRole="text"
      accessibilityHint="Tato objednávka má vysokou prioritu"
      // === ARIA atributy (web) ===
      aria-label="VIP objednávka"
      // === CLASSNAME pro CSS selektory ===
      className="priority-badge vip-badge badge-high"
    >
      <MaterialIcons
        name="star"
        size={14}
        color="#ffc107"
        // === ICON LOKÁTORY ===
        testID={testID ? `${testID}-icon` : 'priority-badge-vip-icon'}
        nativeID="priority-star-icon"
        data-component="priority-icon"
        data-icon="star"
        accessibilityLabel="Hvězdička VIP"
      />
      <Text
        style={styles.text}
        // === VIP TEXT LOKÁTORY ===
        testID={testID ? `${testID}-text` : 'priority-badge-vip-text'}
        nativeID="priority-vip-text"
        id="vip-label"
        data-component="priority-text"
        data-class="priority-label vip-text"
        accessibilityRole="text"
        className="priority-label vip-text"
      >
        VIP
      </Text>
    </View>
  );
};

const styles = StyleSheet.create({
  // Kontejner VIP badge
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff8e1',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#ffc107',
    gap: 4,
  },
  // VIP text
  text: {
    color: '#ff8f00',
    fontSize: 11,
    fontWeight: 'bold',
    textTransform: 'uppercase',
  },
});

export default PriorityBadge;
