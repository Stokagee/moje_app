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
      <View
        style={styles.backdrop}
        // === BACKDROP LOKÁTORY ===
        testID={`${testID}-backdrop`}
        nativeID={`${testID}-backdrop`}
        id={`modal-backdrop-${testID}`}
        data-testid={`${testID}-backdrop`}
        data-component="modal-backdrop"
        data-modal={testID}
        data-class="modal-backdrop overlay"
        accessibilityRole="none"
        aria-hidden="true"
        className="modal-backdrop overlay"
      >
        <View
          style={styles.box}
          // === MODAL BOX LOKÁTORY ===
          testID={`${testID}-box`}
          nativeID={`${testID}-container`}
          id={`modal-${testID}`}
          name={testID}
          data-testid={`${testID}-box`}
          data-component="modal-box"
          data-modal={testID}
          data-class="modal-box modal-container"
          accessibilityRole="none"
          accessibilityLabel={title}
          aria-modal="true"
          aria-labelledby={`${testID}-title`}
          aria-describedby={`${testID}-message`}
          className="modal-box modal-container"
        >
          {title ? (
            <Text
              style={styles.title}
              // === TITLE LOKÁTORY ===
              testID={`${testID}-title`}
              nativeID={`${testID}-title`}
              id={`${testID}-title`}
              data-component="modal-title"
              data-class="modal-title heading"
              accessibilityRole="header"
              className="modal-title heading"
            >
              {title}
            </Text>
          ) : null}
          {message ? (
            <Text
              style={styles.message}
              // === MESSAGE LOKÁTORY ===
              testID={`${testID}-message`}
              nativeID={`${testID}-message`}
              id={`${testID}-message`}
              data-component="modal-message"
              data-class="modal-message body"
              accessibilityRole="text"
              className="modal-message body"
            >
              {message}
            </Text>
          ) : null}

          <View
            style={styles.actions}
            // === ACTIONS CONTAINER LOKÁTORY ===
            testID={`${testID}-actions`}
            nativeID={`${testID}-actions`}
            id={`${testID}-buttons`}
            data-component="modal-actions"
            data-class="modal-actions button-group"
            accessibilityRole="none"
            className="modal-actions button-group"
          >
            {secondaryText && onSecondary ? (
              <TouchableOpacity
                style={[styles.button, styles.secondary]}
                onPress={onSecondary}
                // === SECONDARY BUTTON LOKÁTORY ===
                testID={`${testID}-secondary`}
                nativeID={`${testID}-btn-secondary`}
                id={`${testID}-secondary-btn`}
                name="secondary"
                data-testid={`${testID}-secondary`}
                data-component="modal-button"
                data-action="secondary"
                data-variant="secondary"
                data-class="btn btn-secondary modal-btn"
                accessibilityLabel={secondaryText}
                accessibilityRole="button"
                aria-label={secondaryText}
                className="btn btn-secondary modal-btn"
              >
                <Text
                  style={[styles.buttonText, styles.secondaryText]}
                  testID={`${testID}-secondary-text`}
                  nativeID={`${testID}-secondary-label`}
                  data-component="button-text"
                  data-class="button-label"
                  className="button-label"
                >
                  {secondaryText}
                </Text>
              </TouchableOpacity>
            ) : null}

            <TouchableOpacity
              style={[styles.button, styles.primary]}
              onPress={onPrimary}
              // === PRIMARY BUTTON LOKÁTORY ===
              testID={`${testID}-primary`}
              nativeID={`${testID}-btn-primary`}
              id={`${testID}-primary-btn`}
              name="primary"
              data-testid={`${testID}-primary`}
              data-component="modal-button"
              data-action="primary"
              data-variant="primary"
              data-class="btn btn-primary modal-btn"
              accessibilityLabel={primaryText}
              accessibilityRole="button"
              aria-label={primaryText}
              className="btn btn-primary modal-btn"
            >
              <Text
                style={[styles.buttonText, styles.primaryText]}
                testID={`${testID}-primary-text`}
                nativeID={`${testID}-primary-label`}
                data-component="button-text"
                data-class="button-label"
                className="button-label"
              >
                {primaryText}
              </Text>
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
