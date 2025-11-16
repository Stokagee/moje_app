import React, { useState } from 'react';
import { TextInput, StyleSheet, View, Text } from 'react-native';

const Input = ({
  placeholder,
  value,
  onChangeText,
  keyboardType = 'default',
  testID,
  error,
  errorMessage,
  required,
  onValidation,
  validationType, // 'email', 'phone', etc.
  touched = false
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const [hasBeenTouched, setHasBeenTouched] = useState(touched);

  // Validace emailu
  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  // Validace telefonu (základní - jen čísla)
  const validatePhone = (phone) => {
    const phoneRegex = /^[0-9+\-\s()]+$/;
    return phoneRegex.test(phone) && phone.length >= 9;
  };

  // Určení, zda má být zobrazena chyba
  const shouldShowError = () => {
    if (!hasBeenTouched && !isFocused) return false;

    // Kontrola povinnosti
    if (required && !value?.trim()) {
      return true;
    }

    // Kontrola validace podle typu
    if (value && validationType === 'email' && !validateEmail(value)) {
      return true;
    }

    if (value && validationType === 'phone' && !validatePhone(value)) {
      return true;
    }

    // Externí error prop
    if (error) return true;

    return false;
  };

  // Získání error zprávy
  const getErrorMessage = () => {
    if (errorMessage) return errorMessage;

    if (required && !value?.trim()) {
      return 'Toto pole je povinné';
    }

    if (validationType === 'email' && value && !validateEmail(value)) {
      return 'Zadejte platnou emailovou adresu';
    }

    if (validationType === 'phone' && value && !validatePhone(value)) {
      return 'Zadejte platné telefonní číslo';
    }

    return '';
  };

  // Handler pro focus
  const handleFocus = () => {
    setIsFocused(true);
  };

  // Handler pro blur
  const handleBlur = () => {
    setIsFocused(false);
    setHasBeenTouched(true);

    // Volání validační funkce
    if (onValidation) {
      onValidation(value, shouldShowError());
    }
  };

  const showError = shouldShowError();
  const currentErrorMessage = getErrorMessage();

  return (
    <View style={styles.container}>
      <TextInput
        style={[
          styles.input,
          showError && styles.inputError,
          isFocused && styles.inputFocused
        ]}
        placeholder={placeholder}
        value={value}
        onChangeText={onChangeText}
        keyboardType={keyboardType}
        testID={testID}
        onFocus={handleFocus}
        onBlur={handleBlur}
      />

      {showError && currentErrorMessage && (
        <Text style={styles.errorText} testID={`${testID}-error`}>
          {currentErrorMessage}
        </Text>
      )}
    </View>
  );
};

// Styles for the reusable text input component.
// These values are chosen to match the overall app rhythm:
// - height: visual height of the control (touch target and alignment with other controls)
// - borderColor / borderWidth: subtle outline to separate the field from background
// - borderRadius: rounded corners for a friendly UI
// - marginBottom: spacing to the next element in vertical layout
// - paddingHorizontal: internal horizontal padding for the text content
const styles = StyleSheet.create({
  container: {
    marginBottom: 15, // celková mezera pro kontejner včetně error textu
  },
  input: {
    height: 40, // výška textového pole: konzistentní s ostatními prvky a dostatečný dotykový cíl
    borderColor: '#ccc', // barva okraje: jemné oddělení od pozadí
    borderWidth: 1, // šířka okraje: vizuální oddělovač pole
    borderRadius: 5, // zaoblení rohů: sjednocuje vzhled s ostatními ovládacími prvky
    paddingHorizontal: 10, // horizontální vnitřní odsazení: prostor pro text od okrajů
    backgroundColor: '#fff', // bílé pozadí
  },
  inputFocused: {
    borderColor: '#007AFF', // modré ohraničení při focusu
    borderWidth: 2, // silnější ohraničení při focusu
  },
  inputError: {
    borderColor: '#FF3B30', // červené ohraničení při chybě
    borderWidth: 2, // silnější ohraničení při chybě
  },
  errorText: {
    color: '#FF3B30', // červená barva pro error text
    fontSize: 12, // menší velikost písma
    marginTop: 5, // mezera nad error textem
    marginLeft: 2, // malé odsazení zleva
  },
});

export default Input;