import React from 'react';
import { TouchableOpacity, Text, StyleSheet } from 'react-native';

const Button = ({
  title,
  onPress,
  testID,
  color = 'green',
  variant = 'primary',  // primary, secondary, danger, success
  action = 'submit',    // submit, cancel, delete, refresh, back
  disabled = false
}) => {
  // Extrahování názvu akce z testID
  const buttonName = testID ? testID.replace('Button', '') : action;

  return (
    <TouchableOpacity
      style={[
        styles.button,
        { backgroundColor: color },
        disabled && styles.disabled
      ]}
      onPress={onPress}
      disabled={disabled}
      // === TESTID - React Native standard ===
      testID={testID}
      // === NATIVEID - mapuje se na id ve webu ===
      nativeID={`btn-${buttonName}`}
      // === ID - explicitní HTML id ===
      id={`button-${buttonName}`}
      // === NAME - název tlačítka ===
      name={buttonName}
      // === DATA-* atributy pro CSS selektory ===
      data-testid={testID}
      data-component="button"
      data-action={action}
      data-variant={variant}
      data-disabled={disabled ? 'true' : 'false'}
      data-class={`btn btn-${variant}`}
      // === ACCESSIBILITY atributy ===
      accessibilityLabel={title}
      accessibilityRole="button"
      accessibilityHint={`Klikněte pro ${action}`}
      accessibilityState={{ disabled: disabled }}
      // === ARIA atributy (web) ===
      aria-label={title}
      aria-disabled={disabled}
      aria-pressed={false}
      // === CLASSNAME pro CSS selektory ===
      className={`btn btn-${variant} btn-${buttonName} ${disabled ? 'btn-disabled' : ''}`}
    >
      <Text
        style={styles.buttonText}
        // === BUTTON TEXT LOKÁTORY ===
        testID={testID ? `${testID}-text` : undefined}
        nativeID={`btn-text-${buttonName}`}
        data-component="button-text"
        data-class="button-label"
        accessibilityRole="text"
        className="button-text button-label"
      >
        {title}
      </Text>
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
  disabled: {
    opacity: 0.5, // snížená průhlednost pro disabled stav
  },
});

export default Button;