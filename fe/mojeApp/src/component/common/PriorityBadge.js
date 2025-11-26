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
      testID={testID}
      nativeID={testID}
      accessibilityLabel="VIP objednavka"
      accessibilityRole="text"
      data-class="priority-badge vip"
      data-priority="high"
    >
      <MaterialIcons name="star" size={14} color="#ffc107" />
      <Text style={styles.text}>VIP</Text>
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
