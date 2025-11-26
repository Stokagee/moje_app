import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Container from '../layout/Container';
import NiceList from '../common/List';
import Button from '../common/Button';
import InfoModal from '../common/InfoModal';
import useAppModal from '../context/useAppModal';

// Dynamická konfigurace API URL podle platformy
const getApiUrl = () => {
  // Pro web
  if (typeof window !== 'undefined' && window.location) {
    return 'http://localhost:8000';
  }
  // Pro React Native (mobil)
  return 'http://10.0.2.2:8000'; // Android emulator
};

const API_URL = getApiUrl();

export default function Page2({ navigation }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [infoModalVisible, setInfoModalVisible] = useState(false);
  const [selectedUserData, setSelectedUserData] = useState(null);
  const { showModal } = useAppModal();

  // Načtení dat z API
  const loadData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/v1/form/`);
      const result = await response.json();

      if (response.ok) {
        // Transformace dat do formátu pro NiceList
        const transformedData = result.map((item, index) => ({
          id: item.id || index + 1,
          fullName: `${item.first_name} ${item.last_name}`,
          selected: false, // Defaultně nevybrané
          originalData: item // Uchování původních dat pro pozdější použití
        }));
        setData(transformedData);
      } else {
        showModal({
          title: 'Chyba',
          message: 'Nepodařilo se načíst data',
          primaryText: 'OK',
          testID: 'loadDataErrorModal',
        });
      }
    } catch (error) {
      showModal({
        title: 'Chyba',
        message: 'Došlo k chybě při načítání dat',
        primaryText: 'OK',
        testID: 'loadDataExceptionModal',
      });
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Toggle checkboxu
  const handleToggle = (id) => {
    setData(prevData =>
      prevData.map(item =>
        item.id === id ? { ...item, selected: !item.selected } : item
      )
    );
  };

  // Otevření info modalu s daty uživatele
  const handleNamePress = async (item) => {
    const user = item.originalData;
    // načti attachments a připrav data pro modal
    let hasFile = false;
    let instructions = '';
    try {
      const resp = await fetch(`${API_URL}/api/v1/form/${user.id}/attachments`);
      const atts = await resp.json();
      hasFile = Array.isArray(atts) && atts.length > 0;
      // nejprve zkus načíst samostatné instrukce
      try {
        const instResp = await fetch(`${API_URL}/api/v1/form/${user.id}/instructions`);
        if (instResp.ok) {
          const inst = await instResp.json();
          if (inst && inst.text) {
            instructions = inst.text;
          }
        }
      } catch (_) {
        // ignore
      }
      // pokud nejsou zvlášť, fallback na instrukce uložené u přílohy
      if (!instructions && hasFile) {
        instructions = atts[0]?.instructions || '';
      }
    } catch (e) {
      hasFile = false;
      instructions = '';
    }
    setSelectedUserData({ ...user, _hasFile: hasFile, _instructions: instructions });
    setInfoModalVisible(true);
  };

  // Zavření info modalu
  const handleCloseInfoModal = () => {
    setInfoModalVisible(false);
    setSelectedUserData(null);
  };

  // Smazání položky
  const handleDelete = async (id) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/form/${id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        // Odebrání položky z lokálního stavu
        setData(prevData => prevData.filter(item => item.id !== id));

        showModal({
          title: 'Úspěch',
          message: 'Položka byla úspěšně smazána.',
          primaryText: 'OK',
          testID: 'deleteSuccessModal',
        });
      } else {
        throw new Error('Nepodařilo se smazat položku');
      }
    } catch (error) {
      showModal({
        title: 'Chyba',
        message: error.message || 'Došlo k chybě při mazání',
        primaryText: 'OK',
        testID: 'deleteErrorModal',
      });
    }
  };

  // Načtení dat při prvním renderu
  useEffect(() => {
    loadData();
  }, []);

  // Zobrazení loading stavu
  if (loading) {
    return (
      <Container>
        <View
          style={styles.center}
          // === LOADING CONTAINER LOKÁTORY ===
          testID="page2-loading-container"
          nativeID="page2-loading"
          id="loading-section"
          data-component="loading-container"
          data-page="page2"
          data-state="loading"
          data-class="loading-container center-content"
          accessibilityRole="progressbar"
          accessibilityLabel="Načítání dat"
          aria-label="Načítání dat"
          aria-busy="true"
          className="loading-container center-content"
        >
          <Text
            // === LOADING TEXT LOKÁTORY ===
            testID="page2-loading-text"
            nativeID="page2-loading-text"
            id="loading-text"
            data-component="loading-text"
            data-class="loading-message"
            accessibilityRole="text"
            aria-live="polite"
            className="loading-message"
          >Načítání dat...</Text>
        </View>
      </Container>
    );
  }

  return (
    <Container>
      <Text
        style={styles.title}
        // === PAGE TITLE LOKÁTORY ===
        testID="page2Title"
        nativeID="page2-title"
        id="page2-heading"
        data-component="page-title"
        data-page="page2"
        data-section="list-page"
        data-class="page-title heading main-title"
        accessibilityRole="header"
        accessibilityLabel="Seznam odeslaných formulářů"
        aria-label="Seznam odeslaných formulářů"
        aria-level="1"
        className="page-title heading main-title"
      >Seznam odeslaných formulářů</Text>

      <NiceList
        data={data}
        onToggle={handleToggle}
        onDelete={handleDelete}
        onNamePress={handleNamePress}
      />

      <View
        style={styles.buttonContainer}
        // === BUTTON CONTAINER LOKÁTORY ===
        testID="page2-buttons"
        nativeID="page2-button-container"
        id="button-group"
        data-component="button-container"
        data-page="page2"
        data-class="button-container button-group actions"
        accessibilityRole="group"
        accessibilityLabel="Akční tlačítka"
        aria-label="Akční tlačítka"
        className="button-container button-group actions"
      >
        <Button
          title="Aktualizovat"
          onPress={loadData}
          testID="refreshButton"
          variant="primary"
          action="refresh"
        />
        <Button
          title="Zpět na formulář"
          onPress={() => navigation.navigate('FormPage')}
          color="#666"
          testID="backButton"
          variant="secondary"
          action="navigate-back"
        />
      </View>

      {/* InfoModal pro zobrazení detailů uživatele */}
      <InfoModal
        visible={infoModalVisible}
        onClose={handleCloseInfoModal}
        userData={selectedUserData}
        message={selectedUserData?._hasFile ? 'Soubor nahrán' : 'Soubor nenahrán'}
        variant={selectedUserData?._hasFile ? 'success' : 'warning'}
      />
    </Container>
  );
}

const styles = StyleSheet.create({
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  buttonContainer: {
    marginTop: 20,
    gap: 10,
  },
});