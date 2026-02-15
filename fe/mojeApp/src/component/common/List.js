import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, ScrollView } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';

/**
 * Komponenta zobrazující seznam položek s ID, jménem, checkboxem a tlačítkem pro smazání.
 * 
 * @param {Array} data - Pole objektů s daty pro zobrazení
 * @param {function} onToggle - Funkce volaná při změně stavu checkboxu
 * @param {function} onDelete - Funkce volaná při kliknutí na tlačítko smazat
 * @param {function} onNamePress - Funkce volaná při kliknutí na jméno
 */
const NiceList = ({ data, onToggle, onDelete, onNamePress }) => {
  // Pokud nejsou žádná data, zobrazí se zpráva
  if (!data || data.length === 0) {
    return (
      <View
        style={styles.emptyContainer}
        // === EMPTY STATE LOKÁTORY ===
        testID="list-empty-state"
        nativeID="list-empty"
        id="list-empty-state"
        data-component="empty-state"
        data-type="list-empty"
        data-class="empty-container list-empty"
        accessibilityRole="alert"
        accessibilityLabel="Žádná data k zobrazení"
        aria-live="polite"
        className="empty-container list-empty"
      >
        <Text
          style={styles.emptyText}
          // === EMPTY TEXT LOKÁTORY ===
          testID="list-empty-text"
          nativeID="list-empty-message"
          id="empty-message"
          data-component="empty-message"
          data-class="empty-text"
          accessibilityRole="text"
          className="empty-text"
        >
          Žádná data k zobrazení
        </Text>
      </View>
    );
  }

  return (
    <View
      style={styles.container}
      // === LIST CONTAINER LOKÁTORY ===
      testID="list-container"
      nativeID="list-table"
      id="data-list"
      data-component="data-table"
      data-rows={data.length}
      data-class="table-container list-container"
      accessibilityRole="none"
      aria-label="Seznam položek"
      aria-rowcount={data.length}
      className="table-container list-container"
    >
      {/* Hlavička tabulky */}
      <View
        style={styles.headerRow}
        // === HEADER ROW LOKÁTORY ===
        testID="list-header-row"
        nativeID="list-header"
        id="table-header"
        data-component="table-header"
        data-class="table-header header-row"
        accessibilityRole="none"
        aria-rowindex={0}
        className="table-header header-row"
      >
        <Text
          style={[styles.headerCell, styles.idColumn]}
          // === HEADER CELL - ID ===
          testID="list-header-id"
          nativeID="header-cell-id"
          id="header-id"
          data-component="header-cell"
          data-column="id"
          data-class="table-header-cell header-id"
          accessibilityRole="none"
          aria-sort="none"
          className="table-header-cell header-id"
        >
          ID
        </Text>
        <Text
          style={[styles.headerCell, styles.nameColumn]}
          // === HEADER CELL - NAME ===
          testID="list-header-name"
          nativeID="header-cell-name"
          id="header-name"
          data-component="header-cell"
          data-column="name"
          data-class="table-header-cell header-name"
          accessibilityRole="none"
          className="table-header-cell header-name"
        >
          Celé jméno
        </Text>
        <Text
          style={[styles.headerCell, styles.checkboxColumn]}
          // === HEADER CELL - SELECTED ===
          testID="list-header-selected"
          nativeID="header-cell-selected"
          id="header-selected"
          data-component="header-cell"
          data-column="selected"
          data-class="table-header-cell header-selected"
          accessibilityRole="none"
          className="table-header-cell header-selected"
        >
          Vybrané
        </Text>
        <Text
          style={[styles.headerCell, styles.actionColumn]}
          // === HEADER CELL - ACTION ===
          testID="list-header-action"
          nativeID="header-cell-action"
          id="header-action"
          data-component="header-cell"
          data-column="action"
          data-class="table-header-cell header-action"
          accessibilityRole="none"
          className="table-header-cell header-action"
        >
          Akce
        </Text>
      </View>

      {/* Tělo tabulky s daty */}
      <ScrollView
        style={styles.scrollContainer}
        // === SCROLL CONTAINER LOKÁTORY ===
        testID="list-scroll-container"
        nativeID="list-body"
        id="table-body"
        data-component="table-body"
        data-class="table-body scroll-container"
        accessibilityRole="none"
        className="table-body scroll-container"
      >
        {data.map((item, index) => (
        <View
          key={item.id}
          style={styles.dataRow}
          // === DATA ROW LOKÁTORY ===
          testID={`list-item-${item.id}`}
          nativeID={`list-row-${item.id}`}
          id={`row-${item.id}`}
          name={`row-${item.id}`}
          data-testid={`list-item-${item.id}`}
          data-component="table-row"
          data-row-id={item.id}
          data-row-index={index}
          data-selected={item.selected ? 'true' : 'false'}
          data-class="table-row data-row"
          accessibilityRole="none"
          accessibilityLabel={`Řádek ${index + 1}: ${item.fullName}`}
          aria-rowindex={index + 1}
          className={`table-row data-row row-${item.id} ${item.selected ? 'row-selected' : ''}`}
        >
          {/* Sloupec ID */}
          <Text
            style={[styles.dataCell, styles.idColumn]}
            // === CELL - ID ===
            testID={`list-item-${item.id}-id`}
            nativeID={`list-cell-id-${item.id}`}
            id={`cell-id-${item.id}`}
            name={`id-${item.id}`}
            data-testid={`list-item-${item.id}-id`}
            data-component="table-cell"
            data-column="id"
            data-value={item.id}
            data-row-id={item.id}
            data-class="table-cell cell-id"
            accessibilityRole="none"
            accessibilityLabel={`ID: ${item.id}`}
            aria-colindex={1}
            className="table-cell cell-id"
          >
            {item.id}
          </Text>

          {/* Sloupec s celým jménem */}
          <TouchableOpacity
            style={[styles.dataCell, styles.nameColumn]}
            onPress={() => onNamePress && onNamePress(item)}
            // === CELL - NAME (clickable) ===
            testID={`list-item-${item.id}-name`}
            nativeID={`list-cell-name-${item.id}`}
            id={`cell-name-${item.id}`}
            name={`name-${item.id}`}
            data-testid={`list-item-${item.id}-name`}
            data-component="table-cell-clickable"
            data-column="name"
            data-value={item.fullName}
            data-row-id={item.id}
            data-action="show-detail"
            data-class="table-cell cell-name clickable"
            accessibilityLabel={item.fullName}
            accessibilityRole="button"
            accessibilityHint="Klikněte pro zobrazení detailu"
            aria-colindex={2}
            className="table-cell cell-name clickable"
          >
            <Text
              style={styles.nameText}
              numberOfLines={1}
              // === NAME TEXT ===
              testID={`list-item-${item.id}-name-text`}
              nativeID={`list-name-text-${item.id}`}
              data-component="cell-text"
              data-class="name-text"
              className="name-text cell-text"
            >
              {item.fullName}
            </Text>
          </TouchableOpacity>

          {/* Sloupec s checkboxem */}
          <View
            style={[styles.dataCell, styles.checkboxColumn]}
            // === CELL - CHECKBOX CONTAINER ===
            testID={`list-item-${item.id}-checkbox-cell`}
            nativeID={`list-cell-checkbox-${item.id}`}
            id={`cell-checkbox-${item.id}`}
            data-component="table-cell"
            data-column="selected"
            data-class="table-cell cell-checkbox"
            accessibilityRole="none"
            aria-colindex={3}
            className="table-cell cell-checkbox"
          >
            <TouchableOpacity
              onPress={() => onToggle(item.id)}
              // === CHECKBOX BUTTON ===
              testID={`list-item-${item.id}-checkbox`}
              nativeID={`list-checkbox-${item.id}`}
              id={`checkbox-${item.id}`}
              name={`selected-${item.id}`}
              data-testid={`list-item-${item.id}-checkbox`}
              data-component="checkbox"
              data-checked={item.selected ? 'true' : 'false'}
              data-row-id={item.id}
              data-action="toggle"
              data-class="checkbox list-checkbox"
              accessibilityLabel={item.selected ? "Vybráno" : "Nevybráno"}
              accessibilityRole="checkbox"
              accessibilityState={{ checked: item.selected }}
              accessibilityHint="Klikněte pro změnu výběru"
              aria-checked={item.selected}
              className={`checkbox list-checkbox ${item.selected ? 'checkbox-checked' : 'checkbox-unchecked'}`}
            >
              <MaterialIcons
                name={item.selected ? 'check-box' : 'check-box-outline-blank'}
                size={24}
                color={item.selected ? '#007AFF' : '#ccc'}
                testID={`list-item-${item.id}-checkbox-icon`}
                nativeID={`list-checkbox-icon-${item.id}`}
                data-component="checkbox-icon"
                data-checked={item.selected ? 'true' : 'false'}
              />
            </TouchableOpacity>
          </View>

          {/* Sloupec s tlačítkem pro smazání */}
          <View
            style={[styles.dataCell, styles.actionColumn]}
            // === CELL - ACTION CONTAINER ===
            testID={`list-item-${item.id}-action-cell`}
            nativeID={`list-cell-action-${item.id}`}
            id={`cell-action-${item.id}`}
            data-component="table-cell"
            data-column="action"
            data-class="table-cell cell-action"
            accessibilityRole="none"
            aria-colindex={4}
            className="table-cell cell-action"
          >
            <TouchableOpacity
              onPress={() => onDelete(item.id)}
              style={styles.deleteButton}
              // === DELETE BUTTON ===
              testID={`list-item-${item.id}-delete`}
              nativeID={`list-delete-${item.id}`}
              id={`delete-${item.id}`}
              name={`delete-${item.id}`}
              data-testid={`list-item-${item.id}-delete`}
              data-component="delete-button"
              data-action="delete"
              data-row-id={item.id}
              data-class="btn btn-delete btn-icon"
              accessibilityLabel="Smazat položku"
              accessibilityRole="button"
              accessibilityHint={`Smazat ${item.fullName}`}
              aria-label={`Smazat ${item.fullName}`}
              className="btn btn-delete btn-icon"
            >
              <MaterialIcons
                name="delete"
                size={20}
                color="#FF3B30"
                testID={`list-item-${item.id}-delete-icon`}
                nativeID={`list-delete-icon-${item.id}`}
                data-component="delete-icon"
              />
            </TouchableOpacity>
          </View>
        </View>
      ))}
      </ScrollView>
    </View>
  );
};

// Styly pro komponentu seznamu
const styles = StyleSheet.create({
  // Kontejner celého seznamu
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  // Řádek hlavičky tabulky
  headerRow: {
    flexDirection: 'row',
    backgroundColor: '#f8f9fa',
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderBottomWidth: 2,
    borderBottomColor: '#e9ecef',
  },
  // Řádek s daty
  dataRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f1f3f5',
    minHeight: 50,
  },
  // Buňka hlavičky
  headerCell: {
    fontWeight: 'bold',
    fontSize: 14,
    color: '#495057',
    textAlign: 'center',
  },
  // Buňka s daty
  dataCell: {
    fontSize: 14,
    color: '#212529',
    textAlign: 'center',
    justifyContent: 'center',
    alignItems: 'center',
  },
  // Sloupec ID - šířka 15%
  idColumn: {
    width: '15%',
  },
  // Sloupec jména - šířka 50%
  nameColumn: {
    width: '50%',
    textAlign: 'left',
    paddingLeft: 8,
  },
  // Sloupec checkboxu - šířka 15%
  checkboxColumn: {
    width: '15%',
  },
  // Sloupec akce - šířka 20%
  actionColumn: {
    width: '20%',
  },
  // Tlačítko pro smazání
  deleteButton: {
    padding: 6,
    borderRadius: 5,
    backgroundColor: '#fff1f0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  // Scroll container pro data
  scrollContainer: {
    flex: 1,
  },
  // Kontejner pro prázdný stav
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  // Text prázdného stavu
  emptyText: {
    color: '#666',
    fontSize: 16,
  },
  // Text jména v buňce
  nameText: {
    fontSize: 14,
    color: '#212529',
  },
});

export default NiceList;