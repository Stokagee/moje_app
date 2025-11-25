import React from 'react';
import { TouchableOpacity, Text, StyleSheet } from 'react-native';

const Button = ({ title, onPress, testID, color = 'green' }) => {
  return (
    <TouchableOpacity
      style={[styles.button, { backgroundColor: color }]}
      onPress={onPress}
      testID={testID}
      // Lokátory pro RF demonstraci
      nativeID={testID}
      accessibilityLabel={title}
      accessibilityRole="button"
      data-class="btn btn-primary"
      data-action="submit"
    >
      <Text style={styles.buttonText}>{title}</Text>
    </TouchableOpacity>
  );
};

// Styles for the app's primary button component.
const styles = StyleSheet.create({
  button: {
    padding: 15, // vnitřní odsazení: zvětšuje dotykovou plochu a vizuální váhu
    borderRadius: 5, // zaoblení rohů: zjemňuje vzhled tlačítka
    alignItems: 'center', // horizontální zarovnání: centruje text v tlačítku
    marginVertical: 10, // vertikální mezera: odděluje tlačítko od okolních prvků
  },
  buttonText: {
    color: 'white', // barva textu: zajišťuje dobrý kontrast na barevném pozadí
    fontWeight: 'bold', // typografie: tučné písmo pro lepší čitelnost labelu
  },
});

export default Button;