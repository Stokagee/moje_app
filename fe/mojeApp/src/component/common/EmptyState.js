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
  title = 'Žádná data',
  message,
  action,
  testID = 'empty-state',
}) => {
  return (
    <View
      style={styles.container}
      // === TESTID - React Native standard ===
      testID={testID}
      // === NATIVEID - mapuje se na id ve webu ===
      nativeID={testID}
      // === ID - explicitní HTML id ===
      id="empty-state"
      // === NAME - název komponenty ===
      name="empty-state"
      // === DATA-* atributy pro CSS selektory ===
      data-testid={testID}
      data-component="empty-state"
      data-has-action={action ? 'true' : 'false'}
      data-class="empty-state empty-container"
      // === ACCESSIBILITY atributy ===
      accessibilityLabel={title}
      accessibilityRole="none"
      accessibilityHint={message || 'Žádná data k zobrazení'}
      // === ARIA atributy (web) ===
      aria-label={title}
      aria-live="polite"
      // === CLASSNAME pro CSS selektory ===
      className="empty-state empty-container"
    >
      <MaterialIcons
        name={icon}
        size={64}
        color="#ccc"
        // === ICON LOKÁTORY ===
        testID={`${testID}-icon`}
        nativeID="empty-state-icon"
        id="empty-icon"
        data-component="empty-icon"
        data-icon={icon}
        data-class="empty-icon"
        accessibilityLabel={`Ikona: ${icon}`}
      />

      <Text
        style={styles.title}
        // === TITLE LOKÁTORY ===
        testID={`${testID}-title`}
        nativeID="empty-state-title"
        id="empty-title"
        data-component="empty-title"
        data-class="empty-title heading"
        accessibilityRole="header"
        className="empty-title heading"
      >
        {title}
      </Text>

      {message && (
        <Text
          style={styles.message}
          // === MESSAGE LOKÁTORY ===
          testID={`${testID}-message`}
          nativeID="empty-state-message"
          id="empty-message"
          data-component="empty-message"
          data-class="empty-message description"
          accessibilityRole="text"
          className="empty-message description"
        >
          {message}
        </Text>
      )}

      {action && action.onPress && (
        <TouchableOpacity
          style={styles.actionButton}
          onPress={action.onPress}
          // === ACTION BUTTON LOKÁTORY ===
          testID={`${testID}-action`}
          nativeID="empty-state-action"
          id="empty-action-btn"
          name="empty-action"
          data-testid={`${testID}-action`}
          data-component="action-button"
          data-action="empty-action"
          data-class="btn btn-primary empty-action"
          accessibilityLabel={action.label}
          accessibilityRole="button"
          accessibilityHint="Klikněte pro akci"
          aria-label={action.label}
          className="btn btn-primary empty-action"
        >
          <Text
            style={styles.actionText}
            // === ACTION TEXT LOKÁTORY ===
            testID={`${testID}-action-text`}
            nativeID="empty-action-text"
            id="action-label"
            data-component="button-text"
            data-class="button-label action-label"
            accessibilityRole="text"
            className="button-label action-label"
          >
            {action.label}
          </Text>
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
