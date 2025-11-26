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
        // === OVERLAY LOKÁTORY ===
        testID="info-modal-overlay"
        nativeID="info-modal-overlay"
        id="modal-overlay"
        data-component="modal-overlay"
        data-modal="info"
        data-class="modal-overlay info-overlay"
        accessibilityLabel="Zavřít modal"
        accessibilityRole="none"
        aria-label="Klikněte pro zavření"
        className="modal-overlay info-overlay"
      >
        {/* Obsah modalu - při kliknutí na obsah se modal NEzavře */}
        <TouchableOpacity
          style={styles.modalContainer}
          activeOpacity={1}
          onPress={(e) => e.stopPropagation()}
          // === MODAL CONTAINER LOKÁTORY ===
          testID="info-modal-container"
          nativeID="info-modal-content"
          id="info-modal"
          name="info-modal"
          data-testid="info-modal-container"
          data-component="modal-container"
          data-modal="info"
          data-variant={variant}
          data-class="modal-container info-modal"
          accessibilityRole="dialog"
          accessibilityLabel="Detail uživatele"
          aria-modal="true"
          aria-labelledby="modal-title"
          className="modal-container info-modal"
        >
          {/* Volitelný banner se zprávou (např. tajná hláška) */}
          {message ? (
            <View
              style={[styles.banner, styles[`banner_${variant}`]]}
              // === BANNER LOKÁTORY ===
              testID="info-modal-banner"
              nativeID="info-modal-banner"
              id="modal-banner"
              data-component="modal-banner"
              data-variant={variant}
              data-class={`modal-banner banner-${variant}`}
              accessibilityRole="status"
              accessibilityLabel={`Zpráva: ${message}`}
              aria-live="polite"
              className={`modal-banner banner-${variant}`}
            >
              <MaterialIcons
                name="emoji-emotions"
                size={22}
                color={variant === 'success' ? '#1e7e34' : variant === 'warning' ? '#8a6d3b' : '#0c5460'}
                style={{ marginRight: 8 }}
                testID="info-modal-banner-icon"
                nativeID="banner-icon"
                data-component="banner-icon"
              />
              <Text
                style={[styles.bannerText, styles[`bannerText_${variant}`]]}
                // === BANNER TEXT LOKÁTORY ===
                testID="info-modal-banner-text"
                nativeID="banner-message"
                id="banner-text"
                data-component="banner-text"
                data-class="banner-message"
                accessibilityRole="text"
                className="banner-text banner-message"
              >
                {message}
              </Text>
            </View>
          ) : null}

          {/* Hlavička modalu s titulem a tlačítkem zavřít */}
          <View
            style={styles.header}
            // === HEADER LOKÁTORY ===
            testID="info-modal-header"
            nativeID="modal-header"
            id="modal-header"
            data-component="modal-header"
            data-class="modal-header"
            accessibilityRole="header"
            className="modal-header"
          >
            <Text
              style={styles.title}
              // === TITLE LOKÁTORY ===
              testID="info-modal-title"
              nativeID="modal-title"
              id="modal-title"
              data-component="modal-title"
              data-class="modal-title"
              accessibilityRole="header"
              className="modal-title"
            >
              Detail uživatele
            </Text>
            <TouchableOpacity
              onPress={onClose}
              style={styles.closeButton}
              // === CLOSE BUTTON LOKÁTORY ===
              testID="info-modal-close"
              nativeID="modal-close-btn"
              id="close-modal"
              name="close"
              data-testid="info-modal-close"
              data-component="close-button"
              data-action="close"
              data-class="btn btn-close modal-close"
              accessibilityLabel="Zavřít modal"
              accessibilityRole="button"
              accessibilityHint="Klikněte pro zavření"
              aria-label="Zavřít"
              className="btn btn-close modal-close"
            >
              <MaterialIcons
                name="close"
                size={24}
                color="#666"
                testID="info-modal-close-icon"
                nativeID="close-icon"
                data-component="close-icon"
              />
            </TouchableOpacity>
          </View>

          {/* Oddělovač pod hlavičkou */}
          <View
            style={styles.divider}
            testID="info-modal-divider-top"
            nativeID="divider-top"
            data-component="divider"
            data-class="divider"
            className="divider"
          />

          {/* Tělo modalu s informacemi */}
          <View
            style={styles.content}
            // === CONTENT LOKÁTORY ===
            testID="info-modal-content"
            nativeID="modal-body"
            id="modal-content"
            data-component="modal-content"
            data-class="modal-body info-content"
            accessibilityRole="main"
            className="modal-body info-content"
          >

            {/* Řádek s jménem a příjmením */}
            <View
              style={styles.infoRow}
              testID="info-name-row"
              nativeID="info-row-name"
              id="row-name"
              data-component="info-row"
              data-field="name"
              data-class="info-row row-name"
              accessibilityRole="group"
              accessibilityLabel="Jméno a příjmení"
              className="info-row row-name"
            >
              <MaterialIcons name="person" size={20} color="#007AFF" style={styles.icon} testID="info-name-icon" nativeID="icon-person" data-component="row-icon" />
              <View style={styles.infoTextContainer} data-component="info-text-container">
                <Text style={styles.label} testID="info-name-label" nativeID="label-name" id="label-name" data-component="info-label" data-field="name" data-class="info-label" accessibilityRole="text" className="info-label">Jméno a příjmení</Text>
                <Text style={styles.value} testID="info-name-value" nativeID="value-name" id="value-name" name="fullName" data-component="info-value" data-field="name" data-value={`${userData.first_name} ${userData.last_name}`} data-class="info-value" accessibilityRole="text" className="info-value">
                  {userData.first_name || 'Neznámé'} {userData.last_name || 'Neznámé'}
                </Text>
              </View>
            </View>

            {/* Řádek s telefonním číslem */}
            <View
              style={styles.infoRow}
              testID="info-phone-row"
              nativeID="info-row-phone"
              id="row-phone"
              data-component="info-row"
              data-field="phone"
              data-class="info-row row-phone"
              accessibilityRole="group"
              accessibilityLabel="Telefonní číslo"
              className="info-row row-phone"
            >
              <MaterialIcons name="phone" size={20} color="#007AFF" style={styles.icon} testID="info-phone-icon" nativeID="icon-phone" data-component="row-icon" />
              <View style={styles.infoTextContainer} data-component="info-text-container">
                <Text style={styles.label} testID="info-phone-label" nativeID="label-phone" id="label-phone" data-component="info-label" data-field="phone" data-class="info-label" accessibilityRole="text" className="info-label">Telefonní číslo</Text>
                <Text style={styles.value} testID="info-phone-value" nativeID="value-phone" id="value-phone" name="phone" data-component="info-value" data-field="phone" data-value={userData.phone} data-class="info-value" accessibilityRole="text" className="info-value">
                  {formatPhoneNumber(userData.phone)}
                </Text>
              </View>
            </View>

            {/* Řádek s emailem */}
            <View
              style={styles.infoRow}
              testID="info-email-row"
              nativeID="info-row-email"
              id="row-email"
              data-component="info-row"
              data-field="email"
              data-class="info-row row-email"
              accessibilityRole="group"
              accessibilityLabel="Email"
              className="info-row row-email"
            >
              <MaterialIcons name="email" size={20} color="#007AFF" style={styles.icon} testID="info-email-icon" nativeID="icon-email" data-component="row-icon" />
              <View style={styles.infoTextContainer} data-component="info-text-container">
                <Text style={styles.label} testID="info-email-label" nativeID="label-email" id="label-email" data-component="info-label" data-field="email" data-class="info-label" accessibilityRole="text" className="info-label">Email</Text>
                <Text style={styles.value} testID="info-email-value" nativeID="value-email" id="value-email" name="email" data-component="info-value" data-field="email" data-value={userData.email} data-class="info-value" accessibilityRole="text" className="info-value">
                  {userData.email || 'Není uveden'}
                </Text>
              </View>
            </View>

            {/* Řádek s pohlavím */}
            <View
              style={styles.infoRow}
              testID="info-gender-row"
              nativeID="info-row-gender"
              id="row-gender"
              data-component="info-row"
              data-field="gender"
              data-class="info-row row-gender"
              accessibilityRole="group"
              accessibilityLabel="Pohlaví"
              className="info-row row-gender"
            >
              <MaterialIcons name="wc" size={20} color="#007AFF" style={styles.icon} testID="info-gender-icon" nativeID="icon-gender" data-component="row-icon" />
              <View style={styles.infoTextContainer} data-component="info-text-container">
                <Text style={styles.label} testID="info-gender-label" nativeID="label-gender" id="label-gender" data-component="info-label" data-field="gender" data-class="info-label" accessibilityRole="text" className="info-label">Pohlaví</Text>
                <Text style={styles.value} testID="info-gender-value" nativeID="value-gender" id="value-gender" name="gender" data-component="info-value" data-field="gender" data-value={userData.gender} data-class="info-value" accessibilityRole="text" className="info-value">
                  {getGenderText(userData.gender)}
                </Text>
              </View>
            </View>

            {/* Stav souboru */}
            <View
              style={styles.infoRow}
              testID="info-file-row"
              nativeID="info-row-file"
              id="row-file"
              data-component="info-row"
              data-field="file"
              data-class="info-row row-file"
              accessibilityRole="group"
              accessibilityLabel="Soubor"
              className="info-row row-file"
            >
              <MaterialIcons name="attach-file" size={20} color="#007AFF" style={styles.icon} testID="info-file-icon" nativeID="icon-file" data-component="row-icon" />
              <View style={styles.infoTextContainer} data-component="info-text-container">
                <Text style={styles.label} testID="info-file-label" nativeID="label-file" id="label-file" data-component="info-label" data-field="file" data-class="info-label" accessibilityRole="text" className="info-label">Soubor</Text>
                <Text style={styles.value} testID="info-file-status" nativeID="value-file" id="value-file" name="file" data-component="info-value" data-field="file" data-has-file={userData._hasFile ? 'true' : 'false'} data-class="info-value" accessibilityRole="text" className="info-value">
                  {userData._hasFile ? 'Nahrán' : 'Nenahrán'}
                </Text>
              </View>
            </View>

            {/* Dlouhé instrukce se scrollbarem, pokud jsou k dispozici */}
            {userData._instructions ? (
              <View
                style={{ maxHeight: 160 }}
                testID="info-instructions-section"
                nativeID="info-section-instructions"
                id="section-instructions"
                data-component="info-section"
                data-field="instructions"
                data-has-content="true"
                data-class="info-section instructions-section"
                accessibilityRole="group"
                accessibilityLabel="Instrukce"
                className="info-section instructions-section"
              >
                <Text style={[styles.label, { marginBottom: 6 }]} testID="info-instructions-label" nativeID="label-instructions" id="label-instructions" data-component="info-label" data-field="instructions" data-class="info-label" accessibilityRole="text" className="info-label">Instrukce</Text>
                <ScrollView style={styles.instructionsBox} testID="info-instructions-box" nativeID="instructions-scroll" id="instructions-box" data-component="instructions-box" data-class="instructions-box scroll" accessibilityRole="scrollbar" className="instructions-box">
                  <Text style={styles.instructionsText} testID="info-instructions-text" nativeID="instructions-content" id="instructions-text" name="instructions" data-component="info-value" data-field="instructions" data-class="instructions-text" accessibilityRole="text" className="instructions-text">{userData._instructions}</Text>
                </ScrollView>
              </View>
            ) : (
              <View
                testID="info-instructions-section"
                nativeID="info-section-instructions"
                id="section-instructions"
                data-component="info-section"
                data-field="instructions"
                data-has-content="false"
                data-class="info-section instructions-section empty"
                accessibilityRole="group"
                accessibilityLabel="Instrukce"
                className="info-section instructions-section empty"
              >
                <Text style={[styles.label, { marginBottom: 6 }]} testID="info-instructions-label" nativeID="label-instructions" id="label-instructions" data-component="info-label" data-field="instructions" data-class="info-label" accessibilityRole="text" className="info-label">Instrukce</Text>
                <View style={styles.instructionsBox} testID="info-instructions-box" nativeID="instructions-empty" id="instructions-box" data-component="instructions-box" data-class="instructions-box empty" className="instructions-box empty">
                  <Text style={styles.instructionsText} testID="info-instructions-text" nativeID="instructions-empty-text" id="instructions-text" data-component="info-value" data-field="instructions" data-empty="true" data-class="instructions-text empty" accessibilityRole="text" className="instructions-text empty">Žádné instrukce</Text>
                </View>
              </View>
            )}

          </View>

          {/* Oddělovač nad tlačítkem */}
          <View
            style={styles.divider}
            testID="info-modal-divider-bottom"
            nativeID="divider-bottom"
            data-component="divider"
            data-class="divider"
            className="divider"
          />

          {/* Patička modalu s tlačítkem OK */}
          <View
            style={styles.footer}
            // === FOOTER LOKÁTORY ===
            testID="info-modal-footer"
            nativeID="modal-footer"
            id="modal-footer"
            data-component="modal-footer"
            data-class="modal-footer"
            accessibilityRole="contentinfo"
            className="modal-footer"
          >
            <TouchableOpacity
              onPress={onClose}
              style={styles.okButton}
              // === OK BUTTON LOKÁTORY ===
              testID="info-modal-ok"
              nativeID="modal-ok-btn"
              id="ok-button"
              name="ok"
              data-testid="info-modal-ok"
              data-component="ok-button"
              data-action="confirm"
              data-class="btn btn-primary btn-ok"
              accessibilityLabel="OK - Zavřít modal"
              accessibilityRole="button"
              accessibilityHint="Klikněte pro potvrzení a zavření"
              aria-label="OK"
              className="btn btn-primary btn-ok"
            >
              <Text
                style={styles.okButtonText}
                // === OK BUTTON TEXT LOKÁTORY ===
                testID="info-modal-ok-text"
                nativeID="ok-btn-text"
                id="ok-text"
                data-component="button-text"
                data-class="button-label ok-label"
                accessibilityRole="text"
                className="button-label ok-label"
              >
                OK
              </Text>
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