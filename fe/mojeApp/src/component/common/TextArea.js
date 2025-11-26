import React from 'react';
import { TextInput, StyleSheet, View, Text } from 'react-native';

const TextArea = ({
  value,
  onChangeText,
  placeholder = 'Instrukce…',
  maxLength = 1000,
  error,
  errorMessage,
  testID,
  field = 'instructions',
  label = 'Instrukce',
  page = 'form'
}) => {
  return (
    <View
      // === CONTAINER LOKÁTORY ===
      testID={testID ? `${testID}-container` : 'textarea-container'}
      nativeID={`container-${field}`}
      id={`${field}-container`}
      data-component="textarea-container"
      data-field={field}
      data-class="textarea-wrapper"
      accessibilityRole="none"
      className="textarea-container"
    >
      <TextInput
        style={[styles.input, error && styles.error]}
        placeholder={placeholder}
        value={value}
        onChangeText={onChangeText}
        multiline
        numberOfLines={4}
        maxLength={maxLength}
        textAlignVertical="top"
        // === TESTID - React Native standard ===
        testID={testID}
        // === NATIVEID - mapuje se na id ve webu ===
        nativeID={`textarea-${field}`}
        // === ID - explicitní HTML id ===
        id={field}
        // === NAME - název pole ===
        name={field}
        // === DATA-* atributy pro CSS selektory ===
        data-testid={testID}
        data-field={field}
        data-component="textarea"
        data-page={page}
        data-maxlength={maxLength}
        data-charlength={value?.length || 0}
        data-class="form-textarea textarea-field"
        // === ACCESSIBILITY atributy ===
        accessibilityLabel={placeholder}
        accessibilityRole="text"
        accessibilityHint={`Maximální délka ${maxLength} znaků`}
        accessibilityState={{ disabled: false }}
        // === ARIA atributy (web) ===
        aria-label={label}
        aria-describedby={`${field}-counter ${field}-error`}
        aria-invalid={error}
        aria-multiline={true}
        aria-placeholder={placeholder}
        // === CLASSNAME pro CSS selektory ===
        className={`form-textarea textarea-field ${field}-textarea ${error ? 'textarea-error' : ''}`}
      />
      <View
        style={styles.footerRow}
        // === FOOTER ROW LOKÁTORY ===
        testID={`${testID}-footer`}
        nativeID={`${field}-footer`}
        data-component="textarea-footer"
        data-class="textarea-footer"
        className="textarea-footer"
      >
        <Text
          style={styles.counter}
          // === COUNTER LOKÁTORY ===
          testID={`${testID}-counter`}
          nativeID={`${field}-counter`}
          id={`${field}-counter`}
          data-component="char-counter"
          data-current={value?.length || 0}
          data-max={maxLength}
          data-class="char-counter"
          accessibilityRole="status"
          accessibilityLabel={`${value?.length || 0} z ${maxLength} znaků`}
          aria-live="polite"
          className="char-counter textarea-counter"
        >
          {(value?.length || 0)} / {maxLength}
        </Text>
        {error ? (
          <Text
            style={styles.errorText}
            // === ERROR TEXT LOKÁTORY ===
            testID={`${testID}-error`}
            nativeID={`${field}-error`}
            id={`error-${field}`}
            data-component="error-message"
            data-field={field}
            data-class="error-text validation-error"
            accessibilityRole="alert"
            accessibilityLabel={`Chyba: ${errorMessage}`}
            aria-live="assertive"
            className="error-text validation-error"
          >
            {errorMessage}
          </Text>
        ) : null}
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    padding: 12,
    minHeight: 96,
    backgroundColor: 'white',
    marginBottom: 8,
  },
  error: {
    borderColor: '#ff5757',
  },
  errorText: {
    color: '#ff5757',
    fontSize: 12,
  },
  footerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  counter: {
    color: '#888',
    fontSize: 12,
  },
});

export default TextArea;
