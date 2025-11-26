import React, { useRef, useState } from 'react';
import { Platform, View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import * as DocumentPicker from 'expo-document-picker';
import * as FileSystem from 'expo-file-system';

// Web: využijeme input type=file + drag&drop
// Native: základ – necháme vybrat přes input (Expo web), pro RN native lze doplnit expo-document-picker

const MAX_BYTES = 1 * 1024 * 1024; // 1MB

const FileUploader = ({ accept = '.txt,.pdf', onFileSelected, label = 'Přiložit soubor (.txt, .pdf)', testID = 'file-uploader', onError }) => {
  const inputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);
  const isWeb = Platform.OS === 'web';

  const handleFiles = (files) => {
    if (!files || files.length === 0) return;
    const file = files[0];
    if (!isAllowedType(file.name, accept)) {
      onError && onError('Nepovolený typ souboru. Povolené: .txt, .pdf');
      return;
    }
    if (file.size && file.size > MAX_BYTES) {
      onError && onError('Soubor je příliš velký (max 1MB).');
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      const arrayBuffer = reader.result;
      // převod do base64
      const bytes = new Uint8Array(arrayBuffer);
      let binary = '';
      for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
      const base64 = btoa(binary);
      onFileSelected && onFileSelected({
        name: file.name,
        type: file.type || inferContentType(file.name),
        size: file.size,
        base64,
      });
    };
    reader.readAsArrayBuffer(file);
  };

  const inferContentType = (name) => {
    const lower = name.toLowerCase();
    if (lower.endsWith('.pdf')) return 'application/pdf';
    if (lower.endsWith('.txt')) return 'text/plain';
    return 'application/octet-stream';
  };

  const isAllowedType = (name, acceptList) => {
    const lower = name.toLowerCase();
    const allowed = acceptList.split(',').map(s => s.trim().toLowerCase());
    return allowed.some(ext => lower.endsWith(ext));
  };

  if (!isWeb) {
    // Native: DocumentPicker + FileSystem (base64)
    const pickDocument = async () => {
      try {
        const res = await DocumentPicker.getDocumentAsync({ type: ['application/pdf', 'text/plain'] });
        if (res.canceled) return;
        const file = res.assets && res.assets[0];
        if (!file) return;
        const { name, mimeType, size, uri } = file;
        if (!isAllowedType(name, accept)) {
          onError && onError('Nepovolený typ souboru. Povolené: .txt, .pdf');
          return;
        }
        if (size && size > MAX_BYTES) {
          onError && onError('Soubor je příliš velký (max 1MB).');
          return;
        }
        // Přečti do base64
        const base64 = await FileSystem.readAsStringAsync(uri, { encoding: FileSystem.EncodingType.Base64 });
        onFileSelected && onFileSelected({
          name,
          type: mimeType || inferContentType(name),
          size,
          base64,
        });
      } catch (e) {
        onError && onError('Nepodařilo se vybrat soubor.');
      }
    };
    return (
      <View
        style={styles.nativeBox}
        // === CONTAINER LOKÁTORY (NATIVE) ===
        testID={`${testID}-container`}
        nativeID="file-uploader-container"
        id="file-uploader"
        data-component="file-uploader"
        data-platform="native"
        data-class="file-uploader-wrapper"
        accessibilityRole="none"
        className="file-uploader-container native"
      >
        <Text
          style={styles.label}
          // === LABEL LOKÁTORY ===
          testID={`${testID}-label`}
          nativeID="file-uploader-label"
          id="file-label"
          data-component="label"
          data-for="file-input"
          data-class="form-label file-label"
          accessibilityRole="text"
          className="form-label file-label"
        >
          {label}
        </Text>
        <TouchableOpacity
          onPress={pickDocument}
          style={styles.pickButton}
          // === TESTID - React Native standard ===
          testID={`${testID}-pick-button`}
          // === NATIVEID - mapuje se na id ve webu ===
          nativeID="file-pick-button"
          // === ID - explicitní HTML id ===
          id="file-picker-btn"
          // === NAME - název tlačítka ===
          name="file-picker"
          // === DATA-* atributy pro CSS selektory ===
          data-testid={`${testID}-pick-button`}
          data-component="file-picker-button"
          data-action="pick-file"
          data-accept={accept}
          data-class="btn file-picker-btn"
          // === ACCESSIBILITY atributy ===
          accessibilityLabel="Vybrat soubor"
          accessibilityRole="button"
          accessibilityHint="Klikněte pro výběr souboru z úložiště"
          // === ARIA atributy (web) ===
          aria-label="Vybrat soubor"
          // === CLASSNAME pro CSS selektory ===
          className="btn file-picker-btn"
        >
          <Text
            style={styles.pickButtonText}
            // === BUTTON TEXT LOKÁTORY ===
            testID={`${testID}-pick-button-text`}
            nativeID="file-pick-button-text"
            data-component="button-text"
            data-class="button-label"
            accessibilityRole="text"
            className="button-text"
          >
            Vybrat soubor
          </Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View
      // === CONTAINER LOKÁTORY (WEB) ===
      testID={`${testID}-container`}
      nativeID="file-uploader-container"
      id="file-uploader"
      data-component="file-uploader"
      data-platform="web"
      data-class="file-uploader-wrapper"
      accessibilityRole="none"
      className="file-uploader-container web"
    >
      <Text
        style={styles.label}
        // === LABEL LOKÁTORY ===
        testID={`${testID}-label`}
        nativeID="file-uploader-label"
        id="file-label"
        data-component="label"
        data-for="file-input"
        data-class="form-label file-label"
        accessibilityRole="text"
        className="form-label file-label"
      >
        {label}
      </Text>
      <View
        style={[styles.dropZone, dragOver && styles.dropZoneActive]}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          handleFiles(e.dataTransfer.files);
        }}
        onClick={() => inputRef.current && inputRef.current.click()}
        // === TESTID - React Native standard ===
        testID={`${testID}-dropzone`}
        // === NATIVEID - mapuje se na id ve webu ===
        nativeID="file-dropzone"
        // === ID - explicitní HTML id ===
        id="file-dropzone"
        // === NAME - název oblasti ===
        name="dropzone"
        // === DATA-* atributy pro CSS selektory ===
        data-testid={`${testID}-dropzone`}
        data-component="dropzone"
        data-action="upload-file"
        data-dragover={dragOver ? 'true' : 'false'}
        data-accept={accept}
        data-class="dropzone file-dropzone"
        // === ACCESSIBILITY atributy ===
        accessibilityLabel="Oblast pro nahrání souboru - přetáhněte nebo klikněte"
        accessibilityRole="button"
        accessibilityHint="Přetáhněte soubor nebo klikněte pro výběr"
        // === ARIA atributy (web) ===
        aria-label="Oblast pro nahrání souboru"
        aria-describedby="dropzone-hint"
        // === CLASSNAME pro CSS selektory ===
        className={`dropzone file-dropzone ${dragOver ? 'dropzone-active' : ''}`}
      >
        <Text
          style={styles.dropText}
          // === DROP TEXT LOKÁTORY ===
          testID={`${testID}-dropzone-text`}
          nativeID="dropzone-hint"
          id="dropzone-hint"
          data-component="dropzone-hint"
          data-class="dropzone-text hint"
          accessibilityRole="text"
          className="dropzone-text hint"
        >
          Přetáhni soubor sem nebo klikni pro výběr
        </Text>
      </View>
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        style={{ display: 'none' }}
        onChange={(e) => handleFiles(e.target.files)}
        // === INPUT (HIDDEN) LOKÁTORY ===
        data-testid={`${testID}-input`}
        id="file-input"
        name="file"
        aria-label="Vybrat soubor"
        aria-hidden="true"
        className="file-input hidden"
      />
    </View>
  );
};

const styles = StyleSheet.create({
  label: {
    fontWeight: 'bold',
    marginBottom: 6,
  },
  dropZone: {
    borderWidth: 2,
    borderStyle: 'dashed',
    borderColor: '#999',
    borderRadius: 8,
    padding: 16,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#fafafa',
    cursor: 'pointer',
  },
  dropZoneActive: {
    borderColor: '#007AFF',
    backgroundColor: '#f0f8ff',
  },
  dropText: {
    color: '#555',
  },
  nativeBox: {
    paddingVertical: 8,
  },
  hint: {
    color: '#777',
    fontSize: 12,
  },
  pickButton: {
    backgroundColor: '#007AFF',
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  pickButtonText: {
    color: 'white',
    fontWeight: 'bold',
  },
});

export default FileUploader;
