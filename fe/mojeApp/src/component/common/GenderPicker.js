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
    <View style={styles.container}>
      {/* Tlačítko pro otevření dropdown menu */}
      <TouchableOpacity
        style={[styles.dropdownButton, error && touched && styles.dropdownButtonError]}
        onPress={toggleDropdown}
        testID={testID}
        // Lokátory pro RF demonstraci
        nativeID="gender-dropdown"
        accessibilityLabel="Výběr pohlaví"
        accessibilityRole="button"
        data-class="dropdown gender-picker"
        data-field="gender"
      >
        {/* Text zobrazující aktuální výběr */}
        <Text style={[styles.buttonText, !value && styles.placeholderText]}>
          {getDisplayText()}
        </Text>
        {/* Ikona šipky (mění se podle stavu menu) */}
        <MaterialIcons 
          name={isVisible ? 'arrow-drop-up' : 'arrow-drop-down'} 
          size={24} 
          color="#666" 
        />
      </TouchableOpacity>

      {/* Error message */}
      {error && touched && errorMessage && (
        <Text style={styles.errorText}>{errorMessage}</Text>
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
        >
          {/* Kontejner s obsahem menu */}
          <View style={styles.modalContent}>
            <ScrollView style={styles.optionsContainer}>
              {/* Mapování možností pohlaví */}
              {options.map((option) => (
                <TouchableOpacity
                  key={option.value}
                  style={styles.option}
                  onPress={() => handleSelect(option.value)}
                  testID={`gender-option-${option.value}`}
                  // Lokátory pro RF demonstraci
                  nativeID={`gender-option-${option.value}`}
                  accessibilityLabel={option.label}
                  accessibilityRole="menuitem"
                  data-class="dropdown-option gender-option"
                  data-value={option.value}
                >
                  {/* Checkbox ikona - zaškrtnutá/nezaškrtnutá */}
                  <MaterialIcons 
                    name={value === option.value ? 'check-box' : 'check-box-outline-blank'} 
                    size={24} 
                    color={value === option.value ? '#007AFF' : '#666'} 
                  />
                  {/* Text možnosti */}
                  <Text style={styles.optionText}>{option.label}</Text>
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