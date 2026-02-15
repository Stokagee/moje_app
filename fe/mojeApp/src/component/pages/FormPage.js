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
import logger from '../../utils/lokiLogger';
import { getApiUrl } from '../../utils/apiConfig';

const FormPage = ({ navigation }) => {
  const { showModal } = useAppModal();

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
        } else if (value.length < 9) {
          error = 'Telefonní číslo musí mít alespoň 9 znaků';
        } else if (value.length > 25) {
          error = 'Telefonní číslo může mít maximálně 25 znaků';
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

  const handleBlur = (field) => {
    setTouched({
      ...touched,
      [field]: true,
    });
  };
  const handleSubmit = async () => {
    // DEBUG: Log pro zjisteni, zda se funkce vola
    console.log('=== handleSubmit called ===');
    console.log('API URL:', getApiUrl());
    console.log('formData:', formData);

    // Validace všech polí
    const newErrors = {};
    let hasErrors = false;

    Object.keys(formData).forEach(field => {
      const error = validateField(field, formData[field]);
      newErrors[field] = error;
      if (error) hasErrors = true;
    });

    setErrors(newErrors);

    console.log('hasErrors:', hasErrors);

    if (hasErrors) {
      console.log('Validation errors:', newErrors);
      Alert.alert('Chyba', 'Musíš vyplnit všechna pole');
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

      const apiUrl = `${getApiUrl()}/api/v1/form/`;
      console.log('Fetching:', apiUrl);
      console.log('Payload:', payload);

      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      console.log('Response status:', response.status);
      const data = await response.json();
      console.log('Response data:', data);

      if (response.ok) {
        // Případná příloha + instrukce (nezávisle na sobě)
        if (selectedFile) {
          try {
            await fetch(`${getApiUrl()}/api/v1/form/${data.id}/attachment`, {
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
            logger.warning('Attachment upload failed', {
              error: e.message,
              formId: data.id,
              filename: selectedFile?.name,
            });
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
            await fetch(`${getApiUrl()}/api/v1/form/${data.id}/instructions`, {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ text: instructions }),
            });
          } catch (e) {
            // tichá chyba – nechceme blokovat flow
            logger.warning('Instructions upload failed', {
              error: e.message,
              formId: data.id,
              hasInstructions: !!instructions,
            });
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
      // DEBUG: Log error
      console.log('=== CATCH ERROR ===');
      console.log('Error:', error.message);
      console.log('Error stack:', error.stack);
      Alert.alert('Chyba', error.message || 'Došlo k chybě při odesílání');

      // Log to Loki with context
      logger.error('Form submission failed', {
        error: error.message,
        stack: error.stack,
        formData: { ...formData, email: undefined }, // Don't log PII
        endpoint: '/api/v1/form/',
      });

      // Use consistent AppModal for all platforms
      showModal({
        title: 'Chyba',
        message: error.message || 'Došlo k chybě při odesílání',
        primaryText: 'OK',
        testID: 'formSubmitErrorModal',
      });
    }
  };

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
      <ScrollView
        contentContainerStyle={styles.formWrapper}
        keyboardShouldPersistTaps="handled"
        // === FORM CONTAINER LOKÁTORY ===
        testID="form-page-container"
        nativeID="form-container"
        id="form-section"
        data-component="form-container"
        data-page="form"
        data-section="form-container"
        data-class="form-wrapper page-content"
        accessibilityRole="none"
        aria-label="Registrační formulář"
        className="form-wrapper page-content"
      >
        <Text
          style={styles.label}
          // === LABEL - firstName LOKÁTORY ===
          testID="label-firstName"
          nativeID="label-firstName"
          id="label-firstName"
          data-component="form-label"
          data-for="firstName"
          data-required="true"
          data-class="form-label label-text"
          accessibilityRole="text"
          aria-label="Jméno"
          className="form-label label-text"
        >Jméno</Text>
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

        <Text
          style={styles.label}
          // === LABEL - lastName LOKÁTORY ===
          testID="label-lastName"
          nativeID="label-lastName"
          id="label-lastName"
          data-component="form-label"
          data-for="lastName"
          data-required="true"
          data-class="form-label label-text"
          accessibilityRole="text"
          aria-label="Příjmení"
          className="form-label label-text"
        >Příjmení</Text>
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

        <Text
          style={styles.label}
          // === LABEL - phone LOKÁTORY ===
          testID="label-phone"
          nativeID="label-phone"
          id="label-phone"
          data-component="form-label"
          data-for="phone"
          data-required="true"
          data-class="form-label label-text"
          accessibilityRole="text"
          aria-label="Telefonní číslo"
          className="form-label label-text"
        >Telefonní číslo</Text>
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

        <Text
          style={styles.label}
          // === LABEL - email LOKÁTORY ===
          testID="label-email"
          nativeID="label-email"
          id="label-email"
          data-component="form-label"
          data-for="email"
          data-required="true"
          data-class="form-label label-text"
          accessibilityRole="text"
          aria-label="Email"
          className="form-label label-text"
        >Email</Text>
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

        <Text
          style={styles.label}
          // === LABEL - gender LOKÁTORY ===
          testID="label-gender"
          nativeID="label-gender"
          id="label-gender"
          data-component="form-label"
          data-for="gender"
          data-required="true"
          data-class="form-label label-text"
          accessibilityRole="text"
          aria-label="Pohlaví"
          className="form-label label-text"
        >Pohlaví</Text>
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
        <View
          style={{ marginTop: 12, marginBottom: 12 }}
          // === FILE UPLOAD SECTION LOKÁTORY ===
          testID="file-upload-section"
          nativeID="file-upload-section"
          id="file-section"
          data-component="file-upload-section"
          data-section="file-upload"
          data-class="file-section upload-container"
          accessibilityRole="none"
          accessibilityLabel="Sekce nahrání souboru"
          aria-label="Sekce nahrání souboru"
          className="file-section upload-container"
        >
          <FileUploader
            accept=".txt,.pdf"
            onFileSelected={(file) => setSelectedFile(file)}
            label="Přiložit soubor (.txt, .pdf)"
          />
          {selectedFile ? (
            <Text
              style={{ color: '#555', marginTop: 6 }}
              // === SELECTED FILE TEXT LOKÁTORY ===
              testID="selected-file-text"
              nativeID="selected-file-text"
              id="selected-file"
              data-component="selected-file"
              data-filename={selectedFile.name}
              data-class="selected-file file-name"
              accessibilityRole="text"
              accessibilityLabel={`Vybraný soubor: ${selectedFile.name}`}
              aria-label={`Vybraný soubor: ${selectedFile.name}`}
              className="selected-file file-name"
            >Vybráno: {selectedFile.name}</Text>
          ) : null}
        </View>

        {/* Instrukce */}
        <Text
          style={styles.label}
          // === LABEL - instructions LOKÁTORY ===
          testID="label-instructions"
          nativeID="label-instructions"
          id="label-instructions"
          data-component="form-label"
          data-for="instructions"
          data-required="false"
          data-class="form-label label-text"
          accessibilityRole="text"
          aria-label="Instrukce"
          className="form-label label-text"
        >Instrukce</Text>
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