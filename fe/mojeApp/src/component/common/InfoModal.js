import React from 'react';
import { View, Text, Modal, TouchableOpacity, StyleSheet, ScrollView } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';

/**
 * Informativní modal pro zobrazení detailních informací o uživateli.
 * 
 * @param {boolean} visible - Určuje, zda je modal viditelný
 * @param {function} onClose - Funkce volaná při zavírání modalu
 * @param {Object} userData - Objekt s daty uživatele
 * @param {string} userData.first_name - Křestní jméno
 * @param {string} userData.last_name - Příjmení
 * @param {string} userData.phone - Telefonní číslo
 * @param {string} userData.email - Emailová adresa
 * @param {string} userData.gender - Pohlaví (male/female/other)
 */
const InfoModal = ({ visible, onClose, userData, message, variant = 'info' }) => {
  // Pokud nejsou data, nezobrazí se nic
  if (!userData) return null;

  // Funkce pro formátování telefonního čísla
  const formatPhoneNumber = (phone) => {
    if (!phone) return 'Není uvedeno';
    // Přidá mezeru po každých třech číslicích
    return phone.replace(/(\d{3})(?=\d)/g, '$1 ');
  };

  // Funkce pro překlad pohlaví do češtiny
  const getGenderText = (gender) => {
    switch (gender) {
      case 'male': return 'Muž';
      case 'female': return 'Žena';
      case 'other': return 'Jiné';
      default: return 'Nespecifikováno';
    }
  };

  return (
    <Modal
      visible={visible}
      transparent={true}
      animationType="fade"
      onRequestClose={onClose}
    >
      {/* Překryvná vrstva - při kliknutí mimo modal se zavře */}
      <TouchableOpacity 
        style={styles.overlay}
        activeOpacity={1}
        onPress={onClose}
        testID="easter-egg-modal-overlay"
      >
        {/* Obsah modalu - při kliknutí na obsah se modal NEzavře */}
        <TouchableOpacity 
          style={styles.modalContainer}
          activeOpacity={1}
          onPress={(e) => e.stopPropagation()}
          testID="easter-egg-modal-container"
        >
          {/* Volitelný banner se zprávou (např. tajná hláška) */}
          {message ? (
            <View style={[styles.banner, styles[`banner_${variant}`]]} testID="easter-egg-modal-banner">
              <MaterialIcons name="emoji-emotions" size={22} color={variant === 'success' ? '#1e7e34' : variant === 'warning' ? '#8a6d3b' : '#0c5460'} style={{ marginRight: 8 }} />
              <Text style={[styles.bannerText, styles[`bannerText_${variant}`]]}>{message}</Text>
            </View>
          ) : null}
          
          {/* Hlavička modalu s titulem a tlačítkem zavřít */}
          <View style={styles.header}>
            <Text style={styles.title}>Detail uživatele</Text>
            <TouchableOpacity onPress={onClose} style={styles.closeButton} testID="easter-egg-modal-close">
              <MaterialIcons name="close" size={24} color="#666" />
            </TouchableOpacity>
          </View>

          {/* Oddělovač pod hlavičkou */}
          <View style={styles.divider} />

          {/* Tělo modalu s informacemi */}
          <View style={styles.content}>
            
            {/* Řádek s jménem a příjmením */}
            <View style={styles.infoRow} testID="info-name-row" dataSet={{ testid: 'info-name-row' }}>
              <MaterialIcons name="person" size={20} color="#007AFF" style={styles.icon} />
              <View style={styles.infoTextContainer}>
                <Text style={styles.label} testID="info-name-label" dataSet={{ testid: 'info-name-label' }}>Jméno a příjmení</Text>
                <Text style={styles.value} testID="info-name-value" dataSet={{ testid: 'info-name-value' }}>
                  {userData.first_name || 'Neznámé'} {userData.last_name || 'Neznámé'}
                </Text>
              </View>
            </View>

            {/* Řádek s telefonním číslem */}
            <View style={styles.infoRow} testID="info-phone-row" dataSet={{ testid: 'info-phone-row' }}>
              <MaterialIcons name="phone" size={20} color="#007AFF" style={styles.icon} />
              <View style={styles.infoTextContainer}>
                <Text style={styles.label} testID="info-phone-label" dataSet={{ testid: 'info-phone-label' }}>Telefonní číslo</Text>
                <Text style={styles.value} testID="info-phone-value" dataSet={{ testid: 'info-phone-value' }}>
                  {formatPhoneNumber(userData.phone)}
                </Text>
              </View>
            </View>

            {/* Řádek s emailem */}
            <View style={styles.infoRow} testID="info-email-row" dataSet={{ testid: 'info-email-row' }}>
              <MaterialIcons name="email" size={20} color="#007AFF" style={styles.icon} />
              <View style={styles.infoTextContainer}>
                <Text style={styles.label} testID="info-email-label" dataSet={{ testid: 'info-email-label' }}>Email</Text>
                <Text style={styles.value} testID="info-email-value" dataSet={{ testid: 'info-email-value' }}>
                  {userData.email || 'Není uveden'}
                </Text>
              </View>
            </View>

            {/* Řádek s pohlavím */}
            <View style={styles.infoRow} testID="info-gender-row" dataSet={{ testid: 'info-gender-row' }}>
              <MaterialIcons name="wc" size={20} color="#007AFF" style={styles.icon} />
              <View style={styles.infoTextContainer}>
                <Text style={styles.label} testID="info-gender-label" dataSet={{ testid: 'info-gender-label' }}>Pohlaví</Text>
                <Text style={styles.value} testID="info-gender-value" dataSet={{ testid: 'info-gender-value' }}>
                  {getGenderText(userData.gender)}
                </Text>
              </View>
            </View>

            {/* Stav souboru */}
            <View style={styles.infoRow} testID="info-file-row" dataSet={{ testid: 'info-file-row' }}>
              <MaterialIcons name="attach-file" size={20} color="#007AFF" style={styles.icon} />
              <View style={styles.infoTextContainer}>
                <Text style={styles.label} testID="info-file-label" dataSet={{ testid: 'info-file-label' }}>Soubor</Text>
                <Text style={styles.value} testID="info-file-status" dataSet={{ testid: 'info-file-status' }}>
                  {userData._hasFile ? 'Nahrán' : 'Nenahrán'}
                </Text>
              </View>
            </View>

            {/* Dlouhé instrukce se scrollbarem, pokud jsou k dispozici */}
            {userData._instructions ? (
              <View style={{ maxHeight: 160 }} testID="info-instructions-section" dataSet={{ testid: 'info-instructions-section' }}>
                <Text style={[styles.label, { marginBottom: 6 }]} testID="info-instructions-label" dataSet={{ testid: 'info-instructions-label' }}>Instrukce</Text>
                <ScrollView style={styles.instructionsBox} testID="info-instructions-box" dataSet={{ testid: 'info-instructions-box' }}>
                  <Text style={styles.instructionsText} testID="info-instructions-text" dataSet={{ testid: 'info-instructions-text' }}>{userData._instructions}</Text>
                </ScrollView>
              </View>
            ) : (
              <View testID="info-instructions-section" dataSet={{ testid: 'info-instructions-section' }}>
                <Text style={[styles.label, { marginBottom: 6 }]} testID="info-instructions-label" dataSet={{ testid: 'info-instructions-label' }}>Instrukce</Text>
                <View style={styles.instructionsBox} testID="info-instructions-box" dataSet={{ testid: 'info-instructions-box' }}>
                  <Text style={styles.instructionsText} testID="info-instructions-text" dataSet={{ testid: 'info-instructions-text' }}>Žádné instrukce</Text>
                </View>
              </View>
            )}

          </View>

          {/* Oddělovač nad tlačítkem */}
          <View style={styles.divider} />

          {/* Patička modalu s tlačítkem OK */}
          <View style={styles.footer}>
            <TouchableOpacity onPress={onClose} style={styles.okButton} testID="info-modal-ok">
              <Text style={styles.okButtonText}>OK</Text>
            </TouchableOpacity>
          </View>

        </TouchableOpacity>
      </TouchableOpacity>
    </Modal>
  );
};

// Styly pro informativní modal
const styles = StyleSheet.create({
  // Překryvná vrstva - celá obrazovka s poloprůhledným černým pozadím
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  // Hlavní kontejner modalu - bílé pozadí s zaoblenými rohy
  modalContainer: {
    width: '100%',
    maxWidth: 400,
    backgroundColor: 'white',
    borderRadius: 12,
    overflow: 'hidden',
  },
  // Hlavička modalu - obsahuje název a tlačítko zavřít
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
  },
  // Název modalu v hlavičce
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  // Tlačítko zavřít v pravém horním rohu
  closeButton: {
    padding: 4,
  },
  // Oddělovač mezi sekcemi - tenká šedá čára
  divider: {
    height: 1,
    backgroundColor: '#e0e0e0',
  },
  // Obsah modalu - výpis informací o uživateli
  content: {
    padding: 16,
  },
  // Jeden řádek s informací (ikona + text)
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  // Ikona u každého řádku
  icon: {
    marginRight: 12,
    width: 24,
  },
  // Kontejner pro textové informace
  infoTextContainer: {
    flex: 1,
  },
  // Popisek informace (menší šedý text)
  label: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  // Hodnota informace (větší černý text)
  value: {
    fontSize: 16,
    color: '#333',
    fontWeight: '500',
  },
  // Patička modalu s tlačítkem OK
  footer: {
    padding: 16,
    alignItems: 'center',
  },
  // Tlačítko OK - modré pozadí s bílým textem
  okButton: {
    backgroundColor: '#007AFF',
    paddingHorizontal: 24,
    paddingVertical: 10,
    borderRadius: 6,
    minWidth: 80,
  },
  // Text tlačítka OK
  okButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
  // Banner se zprávou (např. tajná hláška)
  banner: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  banner_info: {
    backgroundColor: '#d1ecf1',
    borderBottomWidth: 1,
    borderBottomColor: '#bee5eb',
  },
  banner_success: {
    backgroundColor: '#d4edda',
    borderBottomWidth: 1,
    borderBottomColor: '#c3e6cb',
  },
  banner_warning: {
    backgroundColor: '#fff3cd',
    borderBottomWidth: 1,
    borderBottomColor: '#ffeeba',
  },
  bannerText: {
    flex: 1,
  },
  bannerText_info: {
    color: '#0c5460',
  },
  bannerText_success: {
    color: '#1e7e34',
  },
  bannerText_warning: {
    color: '#8a6d3b',
  },
  instructionsBox: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 10,
    backgroundColor: '#fafafa',
  },
  instructionsText: {
    color: '#333',
    fontSize: 14,
    lineHeight: 20,
  },
});

export default InfoModal;