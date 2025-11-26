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
  touched = false,
  label,           // label pro aria-label
  page = 'form'    // název stránky pro data-page
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

  // Extrahování názvu pole z testID
  const fieldName = testID ? testID.replace('-input', '') : undefined;

  return (
    <View
      style={styles.container}
      // === CONTAINER LOKÁTORY ===
      testID={testID ? `${testID}-container` : undefined}
      nativeID={fieldName ? `container-${fieldName}` : undefined}
      data-component="input-container"
      data-field={fieldName}
      accessibilityRole="none"
    >
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
        onFocus={handleFocus}
        onBlur={handleBlur}
        // === TESTID - React Native standard ===
        testID={testID}
        // === NATIVEID - mapuje se na id ve webu ===
        nativeID={fieldName ? `input-${fieldName}` : undefined}
        // === ID - explicitní HTML id ===
        id={fieldName}
        // === NAME - název formulářového pole ===
        name={fieldName}
        // === DATA-* atributy pro CSS selektory ===
        data-testid={testID}
        data-field={fieldName}
        data-component="text-input"
        data-page={page}
        data-type={validationType || 'text'}
        data-required={required ? 'true' : 'false'}
        data-class="form-input input-field"
        // === ACCESSIBILITY atributy ===
        accessibilityLabel={placeholder}
        accessibilityRole="text"
        accessibilityHint={required ? 'Povinné pole' : 'Volitelné pole'}
        accessibilityState={{ disabled: false }}
        // === ARIA atributy (web) ===
        aria-label={label || placeholder}
        aria-describedby={fieldName ? `${fieldName}-error` : undefined}
        aria-required={required}
        aria-invalid={showError}
        aria-placeholder={placeholder}
        // === CLASSNAME pro CSS selektory ===
        className={`form-input input-text ${fieldName}-field ${validationType ? `input-${validationType}` : ''}`}
      />

      {showError && currentErrorMessage && (
        <Text
          style={styles.errorText}
          // === ERROR TEXT LOKÁTORY ===
          testID={`${testID}-error`}
          nativeID={fieldName ? `${fieldName}-error` : undefined}
          id={fieldName ? `error-${fieldName}` : undefined}
          data-component="error-message"
          data-field={fieldName}
          data-class="error-text validation-error"
          accessibilityRole="alert"
          accessibilityLabel={`Chyba: ${currentErrorMessage}`}
          aria-live="polite"
          className="error-text validation-error"
        >
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