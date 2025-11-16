import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, ScrollView, Alert } from 'react-native';
import Container from '../layout/Container';
import Input from '../common/Input';
import Button from '../common/Button';
import GenderDropdown from '../common/GenderPicker';
import useAppModal from '../context/useAppModal';
import InfoModal from '../common/InfoModal';
import FileUploader from '../common/FileUploader';
import TextArea from '../common/TextArea';

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

const FormPage = ({ navigation }) => {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    phone: '',
    gender: '',
    email: '',
  });

  const [errors, setErrors] = useState({
    firstName: '',
    lastName: '',
    phone: '',
    gender: '',
    email: '',
  });

  const [touched, setTouched] = useState({
    firstName: false,
    lastName: false,
    phone: false,
    gender: false,
    email: false,
  });

  const [infoVisible, setInfoVisible] = useState(false);
  const [infoUser, setInfoUser] = useState(null);
  const [infoMessage, setInfoMessage] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [instructions, setInstructions] = useState('');

  // Počáteční validace všech polí
  useEffect(() => {
    const initialErrors = {};
    Object.keys(formData).forEach(field => {
      initialErrors[field] = validateField(field, formData[field]);
    });
    setErrors(initialErrors);
  }, []);

  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const validateField = (field, value) => {
    let error = '';

    switch (field) {
      case 'firstName':
        if (!value.trim()) {
          error = 'Uveďte své křestní jméno';
        }
        break;
      case 'lastName':
        if (!value.trim()) {
          error = 'Uveďte své příjmení';
        }
        break;
      case 'phone':
        if (!value.trim()) {
          error = 'Vyplňtě telefonní číslo';
        }
        break;
      case 'email':
        if (!value.trim()) {
          error = 'Vyplňte email';
        } else if (!validateEmail(value)) {
          error = 'Zadejte platnou emailovou adresu';
        }
        break;
      case 'gender':
        if (!value) {
          error = 'Vyberte pohlaví';
        }
        break;
    }

    return error;
  };

  const handleSubmit = async () => {
    // Validace všech polí
    const newErrors = {};
    let hasErrors = false;

    Object.keys(formData).forEach(field => {
      const error = validateField(field, formData[field]);
      newErrors[field] = error;
      if (error) hasErrors = true;
    });

    setErrors(newErrors);

    if (hasErrors) {
      showModal({
        title: 'Chyba',
        message: 'Musíš vyplnit všechna pole',
        primaryText: 'OK',
        testID: 'formValidationModal',
      });
      return;
    }

    try {
      // Map camelCase (frontend) -> snake_case (backend schema)
      const payload = {
        first_name: formData.firstName,
        last_name: formData.lastName,
        phone: formData.phone,
        gender: formData.gender,
        email: formData.email,
      };

      const response = await fetch(`${API_URL}/api/v1/form/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (response.ok) {
        // Případná příloha + instrukce (nezávisle na sobě)
        if (selectedFile) {
          try {
            await fetch(`${API_URL}/api/v1/form/${data.id}/attachment`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                filename: selectedFile.name,
                content_type: selectedFile.type || 'application/octet-stream',
                data_base64: selectedFile.base64,
                // pokud chceš zároveň uložit instrukce s přílohou, necháme je i zde
                instructions: instructions || undefined,
              }),
            });
          } catch (e) {
            // nezastavuj flow – jen informuj do AppModalu
            showModal({
              title: 'Poznámka',
              message: 'Data formuláře uložena, ale přílohu se nepodařilo nahrát.',
              primaryText: 'OK',
              testID: 'uploadWarningModal',
            });
          }
        }

        // Ulož instrukce, i když nebyl nahrán soubor
        if (!selectedFile && instructions && instructions.trim().length > 0) {
          try {
            await fetch(`${API_URL}/api/v1/form/${data.id}/instructions`, {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ text: instructions }),
            });
          } catch (e) {
            // tichá chyba – nechceme blokovat flow
          }
        }

        // Pokud dorazila tajná zpráva, zobraz InfoModal s bannerem a detailem uživatele
        if (data && data.easter_egg && data.secret_message) {
          setInfoUser({
            first_name: data.first_name,
            last_name: data.last_name,
            phone: data.phone,
            email: data.email,
            gender: data.gender,
          });
          setInfoMessage(data.secret_message);
          setInfoVisible(true);
        } else {
          // fallback na globální AppModal
          showModal({
            title: 'Úspěch',
            message: 'Formulář byl úspěšně odeslán.',
            primaryText: 'Pokračovat',
            onPrimary: () => navigation.navigate('Page2'),
            testID: 'formSuccessModal',
          });
        }
      } else {
        throw new Error(data.detail || 'Nepodařilo se odeslat data');
      }
    } catch (error) {
      // Pro web použij window.alert, pro mobil Alert.alert
      if (typeof window !== 'undefined' && window.alert) {
        window.alert(error.message || 'Došlo k chybě při odesílání');
      } else {
        Alert.alert('Chyba', error.message || 'Došlo k chybě při odesílání');
      }
    }
  };

  const { showModal } = useAppModal();

  const updateFormData = (key, value) => {
    // Pro telefonní číslo filtrujeme jen + a číslice
    if (key === 'phone') {
      value = value.replace(/[^+\d]/g, '');
    }

    setFormData({
      ...formData,
      [key]: value,
    });

    // Validace při každé změně hodnoty
    const error = validateField(key, value);
    setErrors({
      ...errors,
      [key]: error,
    });
  };

  return (
    <Container>
      <ScrollView contentContainerStyle={styles.formWrapper}>
        <Text style={styles.label}>Jméno</Text>
        <Input
          placeholder="Zadejte jméno"
          value={formData.firstName}
          onChangeText={(text) => updateFormData('firstName', text)}
          onBlur={() => handleBlur('firstName')}
          error={!!errors.firstName}
          errorMessage={errors.firstName || undefined}
          required={true}
          testID="firstName-input"
        />

        <Text style={styles.label}>Příjmení</Text>
        <Input
          placeholder="Zadejte příjmení"
          value={formData.lastName}
          onChangeText={(text) => updateFormData('lastName', text)}
          onBlur={() => handleBlur('lastName')}
          error={!!errors.lastName}
          errorMessage={errors.lastName || undefined}
          required={true}
          testID="lastName-input"
        />

        <Text style={styles.label}>Telefonní číslo</Text>
        <Input
          placeholder="Zadejte telefon"
          value={formData.phone}
          onChangeText={(text) => updateFormData('phone', text)}
          onBlur={() => handleBlur('phone')}
          error={!!errors.phone}
          errorMessage={errors.phone || undefined}
          required={true}
          keyboardType="phone-pad"
          testID="phone-input"
        />

        <Text style={styles.label}>Email</Text>
        <Input
          placeholder="Zadejte email"
          value={formData.email}
          onChangeText={(text) => updateFormData('email', text)}
          onBlur={() => handleBlur('email')}
          error={!!errors.email}
          errorMessage={errors.email || undefined}
          required={true}
          validationType="email"
          keyboardType="email-address"
          testID="email-input"
        />

        <Text style={styles.label}>Pohlaví</Text>
        <GenderDropdown
          value={formData.gender}
          onSelect={(value) => updateFormData('gender', value)}
          onBlur={() => handleBlur('gender')}
          error={!!errors.gender}
          errorMessage={errors.gender || undefined}
          required={true}
          testID="genderPicker"
        />

        {/* Nahrání souboru */}
        <View style={{ marginTop: 12, marginBottom: 12 }}>
          <FileUploader
            accept=".txt,.pdf"
            onFileSelected={(file) => setSelectedFile(file)}
            label="Přiložit soubor (.txt, .pdf)"
          />
          {selectedFile ? (
            <Text style={{ color: '#555', marginTop: 6 }}>Vybráno: {selectedFile.name}</Text>
          ) : null}
        </View>

        {/* Instrukce */}
        <Text style={styles.label}>Instrukce</Text>
        <TextArea
          value={instructions}
          onChangeText={setInstructions}
          placeholder="Napiš doplňující instrukce…"
          maxLength={1000}
          testID="instructions-textarea"
        />

        <Button title="Odeslat" onPress={handleSubmit}
          style={styles.myButton}
          testID="submitButton" />

        {/* global AppModal is provided by AppModalProvider */}
      </ScrollView>
      {/* InfoModal s tajnou hláškou (použití common komponenty) */}
      <InfoModal
        visible={infoVisible}
        onClose={() => {
          setInfoVisible(false);
          setInfoMessage(null);
          // po zavření můžeme přejít dál
          navigation.navigate('Page2');
        }}
        userData={infoUser}
        message={infoMessage}
        variant="success"
      />
    </Container>
  );
};

const styles = StyleSheet.create({
  label: {
    fontWeight: 'bold',
    marginBottom: 5, // mezera pod popiskem
  },
  myButton: {
    backgroundColor: 'red', // barva tlačítka
    height: 44, // výška tlačítka pro konzistentní dotykový cíl
    width: '100%', // šířka tlačítka: plná šířka kontejneru
    alignSelf: 'stretch', // roztáhne tlačítko v horizontálním směru
    borderRadius: 10, // zaoblení rohů tlačítka
    
  },
  formWrapper: {
    padding: 16, // vnitřní odsazení okolo formuláře
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  col: {
    flex: 1,
    marginRight: 8,
  },
});

export default FormPage;