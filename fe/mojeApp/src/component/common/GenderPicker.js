import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Modal, ScrollView } from 'react-native';
import { MaterialIcons } from '@expo/vector-icons';

/**
 * Komponenta dropdown menu pro výběr pohlaví s checkboxem.
 * Umožňuje výběr z možností: Muž, Žena, Jiné.
 * 
 * @param {string} value - Aktuálně vybraná hodnota ('male', 'female', 'other')
 * @param {function} onSelect - Funkce volaná při změně výběru
 * @param {boolean} error - Indikuje, zda je pole v error stavu
 * @param {string} errorMessage - Chybová zpráva k zobrazení
 * @param {boolean} required - Indikuje, zda je pole povinné
 * @param {function} onBlur - Funkce volaná při opuštění pole
 * @param {string} testID - Identifikátor pro testování
 */
const GenderDropdown = ({ value, onSelect, error, errorMessage, required, onBlur, testID }) => {
  // Stav pro kontrolu viditelnosti dropdown menu
  const [isVisible, setIsVisible] = useState(false);
  // Stav pro sledování, zda bylo pole interaktivní bez výběru
  const [touched, setTouched] = useState(false);
  
  // Definice možností pohlaví
  const options = [
    { label: 'Muž', value: 'male' },
    { label: 'Žena', value: 'female' },
    { label: 'Jiné', value: 'other' },
  ];

  // Přepínání viditelnosti dropdown menu
  const toggleDropdown = () => {
    setIsVisible(!isVisible);
  };

  // Zpracování výběru položky
  const handleSelect = (selectedValue) => {
    onSelect(selectedValue); // Předání vybrané hodnoty nadřazené komponentě
    setIsVisible(false);     // Skrytí dropdown menu po výběru
    setTouched(false);       // Resetovat touched po výběru
    if (onBlur) onBlur();    // Volání onBlur po výběru
  };

  // Handler pro zavření modal bez výběru
  const handleClose = () => {
    setIsVisible(false);
    if (!value) {
      setTouched(true); // Nastavit touched jen pokud není nic vybráno
    }
    if (onBlur) onBlur();    // Volání onBlur při zavření bez výběru
  };

  // Získání textu pro zobrazení na tlačítku
  const getDisplayText = () => {
    const selectedOption = options.find(opt => opt.value === value);
    return selectedOption ? selectedOption.label : 'Vyberte pohlaví';
  };

  return (
    <View
      style={styles.container}
      // === CONTAINER LOKÁTORY ===
      testID="genderPicker-container"
      nativeID="container-gender"
      id="gender-container"
      data-component="dropdown-container"
      data-field="gender"
      data-class="dropdown-wrapper gender-wrapper"
      accessibilityRole="none"
      className="dropdown-container gender-container"
    >
      {/* Tlačítko pro otevření dropdown menu */}
      <TouchableOpacity
        style={[styles.dropdownButton, error && touched && styles.dropdownButtonError]}
        onPress={toggleDropdown}
        // === TESTID - React Native standard ===
        testID={testID}
        // === NATIVEID - mapuje se na id ve webu ===
        nativeID="gender-dropdown"
        // === ID - explicitní HTML id ===
        id="gender-select"
        // === NAME - název pole ===
        name="gender"
        // === DATA-* atributy pro CSS selektory ===
        data-testid={testID}
        data-component="dropdown"
        data-field="gender"
        data-expanded={isVisible ? 'true' : 'false'}
        data-selected={value || 'none'}
        data-required={required ? 'true' : 'false'}
        data-class="dropdown gender-picker"
        // === ACCESSIBILITY atributy ===
        accessibilityLabel="Výběr pohlaví"
        accessibilityRole="button"
        accessibilityHint="Klikněte pro výběr pohlaví"
        accessibilityState={{ expanded: isVisible }}
        // === ARIA atributy (web) ===
        aria-label="Pohlaví"
        aria-expanded={isVisible}
        aria-haspopup="listbox"
        aria-required={required}
        aria-invalid={error && touched}
        // === CLASSNAME pro CSS selektory ===
        className={`dropdown gender-picker ${isVisible ? 'dropdown-open' : 'dropdown-closed'} ${error && touched ? 'dropdown-error' : ''}`}
      >
        {/* Text zobrazující aktuální výběr */}
        <Text
          style={[styles.buttonText, !value && styles.placeholderText]}
          // === DROPDOWN TEXT LOKÁTORY ===
          testID="genderPicker-text"
          nativeID="gender-selected-text"
          id="gender-display"
          data-component="dropdown-text"
          data-selected-value={value || ''}
          data-class="dropdown-value"
          accessibilityRole="text"
          className="dropdown-text gender-value"
        >
          {getDisplayText()}
        </Text>
        {/* Ikona šipky (mění se podle stavu menu) */}
        <MaterialIcons
          name={isVisible ? 'arrow-drop-up' : 'arrow-drop-down'}
          size={24}
          color="#666"
          testID="genderPicker-arrow"
          nativeID="gender-arrow-icon"
          data-component="dropdown-arrow"
          data-expanded={isVisible ? 'true' : 'false'}
          accessibilityLabel={isVisible ? 'Zavřít menu' : 'Otevřít menu'}
        />
      </TouchableOpacity>

      {/* Error message */}
      {error && touched && errorMessage && (
        <Text
          style={styles.errorText}
          // === ERROR TEXT LOKÁTORY ===
          testID="genderPicker-error"
          nativeID="gender-error"
          id="error-gender"
          data-component="error-message"
          data-field="gender"
          data-class="error-text validation-error"
          accessibilityRole="alert"
          accessibilityLabel={`Chyba: ${errorMessage}`}
          aria-live="polite"
          className="error-text validation-error gender-error"
        >
          {errorMessage}
        </Text>
      )}

      {/* Modalní okno s dropdown menu */}
      <Modal
        visible={isVisible}
        transparent
        animationType="fade"
        onRequestClose={handleClose}
      >
        {/* Překryv pro kliknutí mimo menu */}
        <TouchableOpacity
          style={styles.modalOverlay}
          activeOpacity={1}
          onPress={handleClose}
          // === OVERLAY LOKÁTORY ===
          testID="genderPicker-modal-overlay"
          nativeID="gender-modal-overlay"
          id="gender-overlay"
          data-component="modal-overlay"
          data-class="overlay dropdown-overlay"
          accessibilityLabel="Zavřít menu"
          accessibilityRole="none"
          className="modal-overlay dropdown-overlay"
        >
          {/* Kontejner s obsahem menu */}
          <View
            style={styles.modalContent}
            // === MODAL CONTENT LOKÁTORY ===
            testID="genderPicker-modal-content"
            nativeID="gender-modal-content"
            id="gender-listbox"
            data-component="dropdown-listbox"
            data-class="dropdown-menu gender-menu"
            accessibilityRole="none"
            aria-label="Seznam možností pohlaví"
            className="dropdown-menu gender-menu"
          >
            <ScrollView
              style={styles.optionsContainer}
              // === OPTIONS CONTAINER LOKÁTORY ===
              testID="genderPicker-options-list"
              nativeID="gender-options-scroll"
              data-component="options-scroll"
              data-class="options-container"
              accessibilityRole="none"
              className="options-container gender-options"
            >
              {/* Mapování možností pohlaví */}
              {options.map((option, index) => (
                <TouchableOpacity
                  key={option.value}
                  style={styles.option}
                  onPress={() => handleSelect(option.value)}
                  // === TESTID - React Native standard ===
                  testID={`gender-option-${option.value}`}
                  // === NATIVEID - mapuje se na id ve webu ===
                  nativeID={`gender-option-${option.value}`}
                  // === ID - explicitní HTML id ===
                  id={`option-${option.value}`}
                  // === NAME - název možnosti ===
                  name={`gender-${option.value}`}
                  // === DATA-* atributy pro CSS selektory ===
                  data-testid={`gender-option-${option.value}`}
                  data-component="dropdown-option"
                  data-value={option.value}
                  data-index={index}
                  data-selected={value === option.value ? 'true' : 'false'}
                  data-class="dropdown-option gender-option"
                  // === ACCESSIBILITY atributy ===
                  accessibilityLabel={option.label}
                  accessibilityRole="button"
                  accessibilityHint={`Vybrat ${option.label}`}
                  accessibilityState={{ selected: value === option.value }}
                  // === ARIA atributy (web) ===
                  aria-label={option.label}
                  aria-selected={value === option.value}
                  // === CLASSNAME pro CSS selektory ===
                  className={`dropdown-option gender-option option-${option.value} ${value === option.value ? 'option-selected' : ''}`}
                >
                  {/* Checkbox ikona - zaškrtnutá/nezaškrtnutá */}
                  <MaterialIcons
                    name={value === option.value ? 'check-box' : 'check-box-outline-blank'}
                    size={24}
                    color={value === option.value ? '#007AFF' : '#666'}
                    testID={`gender-option-${option.value}-checkbox`}
                    nativeID={`gender-checkbox-${option.value}`}
                    data-component="checkbox-icon"
                    data-checked={value === option.value ? 'true' : 'false'}
                    accessibilityLabel={value === option.value ? 'Zaškrtnuto' : 'Nezaškrtnuto'}
                  />
                  {/* Text možnosti */}
                  <Text
                    style={styles.optionText}
                    // === OPTION TEXT LOKÁTORY ===
                    testID={`gender-option-${option.value}-text`}
                    nativeID={`gender-text-${option.value}`}
                    id={`text-${option.value}`}
                    data-component="option-text"
                    data-value={option.value}
                    data-class="option-label"
                    accessibilityRole="text"
                    className="option-text option-label"
                  >
                    {option.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        </TouchableOpacity>
      </Modal>
    </View>
  );
};

// Styly pro komponentu GenderDropdown
const styles = StyleSheet.create({
  // Hlavní kontejner komponenty
  container: {
    marginBottom: 15, // Spodní mezera pro oddělení od dalšího prvku
  },
  // Tlačítko dropdown menu
  dropdownButton: {
    flexDirection: 'row',          // Rozložení obsahu v řádku
    justifyContent: 'space-between', // Rozložení prostoru mezi obsah
    alignItems: 'center',          // Zarovnání obsahu na střed vertikálně
    height: 40,                    // Výška tlačítka
    borderColor: '#ccc',           // Barva ohraničení
    borderWidth: 1,                // Šířka ohraničení
    borderRadius: 5,               // Zaoblení rohů
    paddingHorizontal: 10,         // Vnitřní horizontální odsazení
    backgroundColor: 'white',      // Barva pozadí
  },
  // Tlačítko dropdown menu v error stavu
  dropdownButtonError: {
    borderColor: '#ff4444',        // Červené ohraničení pro error
    borderWidth: 2,                // Silnější ohraničení při chybě
  },
  // Text tlačítka
  buttonText: {
    fontSize: 16,                  // Velikost písma
    color: '#333',                 // Barva písma
  },
  // Text placeholderu (když není nic vybráno)
  placeholderText: {
    color: '#999',                 // Světlejší barva pro placeholder
  },
  // Error text
  errorText: {
    color: '#ff4444',              // Červená barva pro error
    fontSize: 14,                  // Menší velikost písma
    marginTop: 5,                  // Mezera nad error textem
  },
  // Překryv modalního okna
  modalOverlay: {
    flex: 1,                       // Roztažení na celou plochu
    backgroundColor: 'rgba(0,0,0,0.5)', // Poloprůhledné černé pozadí
    justifyContent: 'center',      // Zarovnání obsahu na střed vertikálně
    alignItems: 'center',          // Zarovnání obsahu na střed horizontálně
  },
  // Obsah modalního okna
  modalContent: {
    width: '80%',                  // Šířka obsahu (80% obrazovky)
    backgroundColor: 'white',      // Bílé pozadí
    borderRadius: 8,               // Zaoblení rohů
    maxHeight: 200,                // Maximální výška
  },
  // Kontejner s možnostmi
  optionsContainer: {
    padding: 10,                   // Vnitřní odsazení
  },
  // Jedna položka možnosti
  option: {
    flexDirection: 'row',          // Rozložení obsahu v řádku
    alignItems: 'center',          // Zarovnání obsahu na střed vertikálně
    paddingVertical: 12,           // Vertikální odsazení
    paddingHorizontal: 8,          // Horizontální odsazení
    borderBottomWidth: 1,          // Spodní ohraničení
    borderBottomColor: '#f0f0f0',  // Barva spodního ohraničení
  },
  // Text možnosti
  optionText: {
    fontSize: 16,                  // Velikost písma
    marginLeft: 10,                // Levý odstup od checkboxu
    color: '#333',                 // Barva písma
  },
});

export default GenderDropdown;