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
      <View style={styles.nativeBox}>
        <Text style={styles.label}>{label}</Text>
        <TouchableOpacity
          onPress={pickDocument}
          testID={`${testID}-pick-button`}
          style={styles.pickButton}
          // Lokátory pro RF demonstraci
          nativeID="file-pick-button"
          accessibilityLabel="Vybrat soubor"
          accessibilityRole="button"
          data-class="btn file-picker-btn"
          data-action="pick-file"
        >
          <Text style={styles.pickButtonText}>Vybrat soubor</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View>
      <Text style={styles.label}>{label}</Text>
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
        testID={`${testID}-dropzone`}
        // Lokátory pro RF demonstraci
        nativeID="file-dropzone"
        accessibilityLabel="Oblast pro nahrání souboru - přetáhněte nebo klikněte"
        accessibilityRole="button"
        data-class="dropzone file-dropzone"
        data-action="upload-file"
      >
        <Text style={styles.dropText}>Přetáhni soubor sem nebo klikni pro výběr</Text>
      </View>
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        style={{ display: 'none' }}
        onChange={(e) => handleFiles(e.target.files)}
        data-testid={`${testID}-input`}
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
  }
});

export default FileUploader;
