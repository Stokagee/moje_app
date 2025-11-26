/**
 * EmptyState - Prazdny stav s ikonou a volitelnou akci
 * Food Delivery System - Phase 1
 */

import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';

/**
 * Prazdny stav - zobrazuje se kdyz nejsou zadna data
 *
 * @param {string} icon - Nazev MaterialIcons ikony
 * @param {string} title - Hlavni nadpis
 * @param {string} message - Popisna zprava
 * @param {object} action - { label: string, onPress: function }
 * @param {string} testID - Test ID pro automatizaci
 */
const EmptyState = ({
  icon = 'inbox',
  title = 'Zadna data',
  message,
  action,
  testID = 'empty-state',
}) => {
  return (
    <View
      style={styles.container}
      testID={testID}
      nativeID={testID}
      accessibilityLabel={title}
      accessibilityRole="text"
      data-class="empty-state"
    >
      <MaterialIcons
        name={icon}
        size={64}
        color="#ccc"
        testID={`${testID}-icon`}
      />

      <Text style={styles.title} testID={`${testID}-title`}>
        {title}
      </Text>

      {message && (
        <Text style={styles.message} testID={`${testID}-message`}>
          {message}
        </Text>
      )}

      {action && action.onPress && (
        <TouchableOpacity
          style={styles.actionButton}
          onPress={action.onPress}
          testID={`${testID}-action`}
          nativeID={`${testID}-action`}
          accessibilityLabel={action.label}
          accessibilityRole="button"
          data-class="btn empty-state-action"
        >
          <Text style={styles.actionText}>{action.label}</Text>
        </TouchableOpacity>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  // Kontejner prazdneho stavu
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
    backgroundColor: '#fafafa',
  },
  // Hlavni nadpis
  title: {
    marginTop: 16,
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    textAlign: 'center',
  },
  // Popisna zprava
  message: {
    marginTop: 8,
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    lineHeight: 20,
  },
  // Akcni tlacitko
  actionButton: {
    marginTop: 20,
    paddingHorizontal: 20,
    paddingVertical: 10,
    backgroundColor: '#007AFF',
    borderRadius: 8,
  },
  // Text akcniho tlacitka
  actionText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
});

export default EmptyState;
