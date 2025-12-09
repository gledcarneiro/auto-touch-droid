import React, { useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, Button, Image, ActivityIndicator, Alert } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import axios from 'axios';

const API_URL = 'http://192.168.1.100:8000/processar_acao'; // Substitua pelo IP da sua máquina onde a API está rodando

export default function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [apiResponse, setApiResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const pickImage = async () => {
    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [4, 3],
      quality: 1,
    });

    if (!result.canceled) {
      setSelectedImage(result.assets[0].uri);
      setApiResponse(null); // Limpa a resposta anterior ao selecionar nova imagem
    }
  };

  const sendImageToApi = async () => {
    if (!selectedImage) {
      Alert.alert('Erro', 'Por favor, selecione uma imagem primeiro.');
      return;
    }

    setLoading(true);
    setApiResponse(null);

    const formData = new FormData();
    formData.append('file', {
      uri: selectedImage,
      name: 'image.jpg',
      type: 'image/jpeg',
    });
    formData.append('action_name', 'pegar_bau'); // O action_name que queremos testar

    try {
      const response = await axios.post(API_URL, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setApiResponse(response.data);
    } catch (error) {
      console.error('Erro ao chamar a API:', error);
      if (error.response) {
        setApiResponse({ error: `Erro da API: ${error.response.status} - ${error.response.data.detail || error.response.data}` });
      } else if (error.request) {
        setApiResponse({ error: 'Erro de rede: Nenhuma resposta recebida da API. Verifique se a API está rodando e o IP está correto.' });
      } else {
        setApiResponse({ error: `Erro: ${error.message}` });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Testador de API AutoTouchDroid</Text>
      <Button title="Selecionar Imagem" onPress={pickImage} />
      {selectedImage && (
        <Image source={{ uri: selectedImage }} style={styles.image} />
      )}
      <Button title="Enviar para API (pegar_bau)" onPress={sendImageToApi} disabled={loading} />
      {loading && <ActivityIndicator size="large" color="#0000ff" style={styles.loadingIndicator} />}
      {apiResponse && (
        <View style={styles.responseContainer}>
          <Text style={styles.responseText}>Resposta da API:</Text>
          <Text>{JSON.stringify(apiResponse, null, 2)}</Text>
        </View>
      )}
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  image: {
    width: 200,
    height: 200,
    marginVertical: 20,
    resizeMode: 'contain',
  },
  responseContainer: {
    marginTop: 20,
    padding: 10,
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 5,
    width: '100%',
  },
  responseText: {
    fontWeight: 'bold',
    marginBottom: 5,
  },
  loadingIndicator: {
    marginVertical: 10,
  },
});
