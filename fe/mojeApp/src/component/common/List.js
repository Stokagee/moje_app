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
      <View style={styles.emptyContainer} testID="list-empty-state">
        <Text style={styles.emptyText}>Žádná data k zobrazení</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Hlavička tabulky */}
      <View style={styles.headerRow}>
        <Text style={[styles.headerCell, styles.idColumn]}>ID</Text>
        <Text style={[styles.headerCell, styles.nameColumn]}>Celé jméno</Text>
        <Text style={[styles.headerCell, styles.checkboxColumn]}>Vybrané</Text>
        <Text style={[styles.headerCell, styles.actionColumn]}>Akce</Text>
      </View>

      {/* Tělo tabulky s daty */}
      <ScrollView style={styles.scrollContainer}>
        {data.map((item) => (
        <View key={item.id} style={styles.dataRow} testID={`list-item-${item.id}`}>
          {/* Sloupec ID */}
          <Text style={[styles.dataCell, styles.idColumn]} testID={`list-item-${item.id}-id`} dataSet={{ testid: `list-item-${item.id}-id` }}>{item.id}</Text>
          
          {/* Sloupec s celým jménem */}
          <TouchableOpacity 
            style={[styles.dataCell, styles.nameColumn]}
            onPress={() => onNamePress && onNamePress(item)}
            testID={`list-item-${item.id}-name`}
          >
            <Text style={styles.nameText} numberOfLines={1}>
              {item.fullName}
            </Text>
          </TouchableOpacity>
          
          {/* Sloupec s checkboxem */}
          <View style={[styles.dataCell, styles.checkboxColumn]}>
            <TouchableOpacity
              onPress={() => onToggle(item.id)}
              testID={`list-item-${item.id}-checkbox`}
            >
              <MaterialIcons 
                name={item.selected ? 'check-box' : 'check-box-outline-blank'} 
                size={24} 
                color={item.selected ? '#007AFF' : '#ccc'} 
              />
            </TouchableOpacity>
          </View>
          
          {/* Sloupec s tlačítkem pro smazání */}
          <View style={[styles.dataCell, styles.actionColumn]}>
            <TouchableOpacity 
              onPress={() => onDelete(item.id)}
              style={styles.deleteButton}
              testID={`list-item-${item.id}-delete`}
            >
              <MaterialIcons name="delete" size={20} color="#FF3B30" />
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
});

export default NiceList;