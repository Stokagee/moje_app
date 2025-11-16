import React from 'react';
import { Modal, View, Text, StyleSheet, TouchableOpacity } from 'react-native';

const AppModal = ({
  visible = false,
  title = '',
  message = '',
  onClose = () => {},
  primaryText = 'OK',
  onPrimary = () => {},
  secondaryText = null,
  onSecondary = null,
  testID = 'appModal',
}) => {
  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={onClose}>
      <View style={styles.backdrop} testID={`${testID}-backdrop`}>
        <View style={styles.box} testID={`${testID}-box`}>
          {title ? <Text style={styles.title} testID={`${testID}-title`}>{title}</Text> : null}
          {message ? <Text style={styles.message} testID={`${testID}-message`}>{message}</Text> : null}

          <View style={styles.actions}>
            {secondaryText && onSecondary ? (
              <TouchableOpacity style={[styles.button, styles.secondary]} onPress={onSecondary} testID={`${testID}-secondary`}>
                <Text style={[styles.buttonText, styles.secondaryText]}>{secondaryText}</Text>
              </TouchableOpacity>
            ) : null}

            <TouchableOpacity style={[styles.button, styles.primary]} onPress={onPrimary} testID={`${testID}-primary`}>
              <Text style={[styles.buttonText, styles.primaryText]}>{primaryText}</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
};

// Styles for the reusable modal component.
// - backdrop: semi-transparent background that centers the modal and prevents interaction
// - box: the visual modal container; constrained with maxWidth for large screens,
//        rounded corners and padding for a friendly look
// - title/message: typography and spacing to separate header and body content
// - actions: lays out buttons horizontally and pins them to the end for common modal UX
// - button / primary / secondary: button sizing and coloring; primary appears more prominent
// - text styles: font sizes and contrast choices for readability
const styles = StyleSheet.create({
  backdrop: {
    flex: 1, // flex: roztažení na celou obrazovku
    backgroundColor: 'rgba(0,0,0,0.5)', // poloprůhledné pozadí: zdůrazňuje modal a blokuje interakci
    justifyContent: 'center', // vertikální centrování obsahu
    alignItems: 'center', // horizontální centrování obsahu
    paddingHorizontal: 70, // horizontální odsazení: zajišťuje okraje na malých obrazovkách
  },
  box: {
    width: '100%', // šířka: plně využije dostupné místo v rámci paddingu backdropu
    maxWidth: 400, // maximální šířka: omezí modal na větších obrazovkách
    backgroundColor: '#bef8f0ff', // barva pozadí modalu
    borderRadius: 50, // silné zaoblení: měkčí vizuální vzhled
    padding: 20, // vnitřní odsazení obsahu modalu
    alignItems: 'center', // centrování obsahu uvnitř boxu
  },
  title: {
    fontSize: 25, // velikost písma titulku
    fontWeight: '700', // tloušťka písma titulku
    marginBottom: 8, // mezera pod titulkem
  },
  message: {
    fontSize: 17, // velikost písma těla zprávy
    color: '#333', // barva textu zprávy
    textAlign: 'center', // centrování textu pro lepší čitelnost
    marginBottom: 16, // spodní mezera před akcemi
  },
  actions: {
    flexDirection: 'row', // rozložení tlačítek vodorovně
    alignSelf: 'stretch', // tlačítka se rozprostřou přes šířku boxu
    justifyContent: 'flex-end', // tlačítka zarovnána vpravo
  },
  button: {
    paddingVertical: 10, // vertikální padding tlačítka pro dostatečný dotykový cíl
    paddingHorizontal: 14, // horizontální padding tlačítka pro vizuální váhu
    borderRadius: 16, // zaoblení tlačítek
    marginLeft: 8, // mezera mezi tlačítky
  },
  primary: {
    backgroundColor: '#2196F3', // barva primárního tlačítka
  },
  secondary: {
    backgroundColor: 'rgba(9, 9, 9, 1)', // barva sekundárního tlačítka
  },
  buttonText: {
    fontSize: 20, // velikost textu tlačítka
  },
  primaryText: {
    color: 'rgba(0, 0, 0, 1)', // barva textu primárního tlačítka
    fontWeight: '600', // tučnost textu primárního tlačítka
  },
  secondaryText: {
    color: '#333', // barva textu sekundárního tlačítka
  },
});

export default AppModal;
