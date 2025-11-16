import React from 'react';
import { TextInput, StyleSheet, View, Text } from 'react-native';

const TextArea = ({ value, onChangeText, placeholder = 'Instrukce…', maxLength = 1000, error, errorMessage, testID }) => {
  return (
    <View>
      <TextInput
        style={[styles.input, error && styles.error]}
        placeholder={placeholder}
        value={value}
        onChangeText={onChangeText}
        multiline
        numberOfLines={4}
        maxLength={maxLength}
        textAlignVertical="top"
        testID={testID}
      />
      <View style={styles.footerRow}>
        <Text style={styles.counter}>{(value?.length || 0)} / {maxLength}</Text>
        {error ? <Text style={styles.errorText}>{errorMessage}</Text> : null}
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
