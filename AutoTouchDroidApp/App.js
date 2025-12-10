import React, { useEffect, useState } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View, Button, ActivityIndicator, Alert, TextInput, ScrollView, Vibration, Pressable } from 'react-native';
import axios from 'axios';
import * as IntentLauncher from 'expo-intent-launcher';

const PACKAGE_NAME = 'com.nplusent.lok'; // Package name do jogo League of Kingdoms

export default function App() {
  const [apiResponse, setApiResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [actionName, setActionName] = useState('pegar_bau');
  const [deviceId, setDeviceId] = useState('');
  const [apiUrl, setApiUrl] = useState('http://127.0.0.1:8000/start_action');
  const [actionsList, setActionsList] = useState([]);
  const [devicesList, setDevicesList] = useState([]);
  const [progress, setProgress] = useState(0);
  const [buttonEnabled] = useState(true);
  const [timerSeconds, setTimerSeconds] = useState(3);
  const [countdown, setCountdown] = useState(0);
  const DEFAULT_BASE = 'http://127.0.0.1:8000';
  const getBaseFromApiUrl = () => {
    if (!apiUrl) return DEFAULT_BASE;
    try {
      return apiUrl.includes('/start_action')
        ? apiUrl.replace('/start_action', '')
        : apiUrl.replace(/\/$/, '');
    } catch {
      return DEFAULT_BASE;
    }
  };

  useEffect(() => {
    const fetchLists = async () => {
      try {
        const base = getBaseFromApiUrl();
        const [a, d] = await Promise.all([
          axios.get(`${base}/actions`),
          axios.get(`${base}/devices`)
        ]);
        setActionsList(a.data.actions || []);
        setDevicesList(d.data.devices || []);
        if (!actionName && a.data.actions && a.data.actions.length) setActionName(a.data.actions[0]);
        if (!deviceId && d.data.devices && d.data.devices.length) setDeviceId(d.data.devices[0]);
      } catch (e) {
        
      }
    };
    fetchLists();
  }, [apiUrl]);

  const openGame = async () => {
    try {
      await IntentLauncher.startActivityAsync('android.intent.action.MAIN', {
        packageName: PACKAGE_NAME,
        category: 'android.intent.category.LAUNCHER',
      });
      Alert.alert('Sucesso', `Jogo ${PACKAGE_NAME} aberto com sucesso!`);
    } catch (error) {
      console.error('Erro ao abrir o jogo:', error);
      Alert.alert('Erro', `Não foi possível abrir o jogo ${PACKAGE_NAME}. Certifique-se de que está instalado.`);
    }
  };

  const startAutomationAction = async () => {
    if (!actionName) {
      Alert.alert('Erro', 'Selecione uma ação.');
      return;
    }
    if (!deviceId) {
      Alert.alert('Erro', 'Selecione um dispositivo.');
      return;
    }

    setLoading(true);
    setApiResponse(null);
    setProgress(0);

    // Contagem regressiva para o usuário alternar manualmente para o jogo
    const total = Math.max(1, Math.min(15, timerSeconds));
    setCountdown(total);
    await new Promise((resolve) => {
      let remaining = total;
      const tick = setInterval(() => {
        remaining = Math.max(0, parseFloat((remaining - 0.5).toFixed(1)));
        setCountdown(remaining);
        if (remaining <= 0) {
          clearInterval(tick);
          resolve();
        }
      }, 500);
    });

    // Verifica estado do jogo antes de executar
    try {
      const base = getBaseFromApiUrl();
      const res = await axios.get(`${base}/check_game_state`, {
        params: { package_name: PACKAGE_NAME, device_id: deviceId }
      });
      const running = !!res.data?.running;
      const foreground = !!res.data?.foreground;
      if (!running || !foreground) {
        Alert.alert('Jogo não em primeiro plano', 'Abra o jogo e tente novamente.');
        setLoading(false);
        return;
      }
    } catch (e) {
      Alert.alert('Falha na verificação', 'Não foi possível verificar o estado do jogo.');
      setLoading(false);
      return;
    }

    const interval = setInterval(() => {
      setProgress((p) => {
        const next = Math.min(100, p + 10);
        return next;
      });
    }, 200);

    const formData = new FormData();
    formData.append('action_name', actionName);
    formData.append('device_id', deviceId);

    try {
      const response = await axios.post(apiUrl, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setApiResponse(response.data);
      Vibration.vibrate(400);
    } catch (error) {
      console.error('Erro ao chamar a API:', error);
      if (error.response) {
        setApiResponse({ error: `Erro da API: ${error.response.status} - ${error.response.data.detail || error.response.data}` });
      } else if (error.request) {
        setApiResponse({ error: 'Erro de rede: Nenhuma resposta recebida da API. Verifique se a API está rodando e o IP está correto.' });
      } else {
        setApiResponse({ error: `Erro: ${error.message}` });
      }
      Vibration.vibrate(800);
    } finally {
      clearInterval(interval);
      setLoading(false);
    }
  };

  

  return (
    <View style={styles.container}>
      <Text style={styles.title}>AutoTouchDroid Controller</Text>

      <View style={styles.selectorHeader}>
        <Text style={styles.selectorTitle}>Ação</Text>
        <Button title="Atualizar" onPress={async () => {
          try {
            const base = getBaseFromApiUrl();
            const res = await axios.get(`${base}/actions`);
            setActionsList(res.data.actions || []);
          } catch {}
        }} />
      </View>
      <ScrollView style={styles.selectorList}>
        {actionsList.map((a) => (
          <Pressable key={a} onPress={() => setActionName(a)} style={[styles.selectorItem, actionName === a && styles.selectorItemActive]}>
            <Text style={styles.selectorItemText}>{a}</Text>
          </Pressable>
        ))}
      </ScrollView>

      <View style={styles.selectorHeader}>
        <Text style={styles.selectorTitle}>Dispositivo</Text>
        <Button title="Atualizar" onPress={async () => {
          try {
            const base = getBaseFromApiUrl();
            const res = await axios.get(`${base}/devices`);
            setDevicesList(res.data.devices || []);
          } catch {}
        }} />
      </View>
      <ScrollView style={styles.selectorList}>
        {devicesList.map((d) => (
          <Pressable key={d} onPress={() => setDeviceId(d)} style={[styles.selectorItem, deviceId === d && styles.selectorItemActive]}>
            <Text style={styles.selectorItemText}>{d}</Text>
          </Pressable>
        ))}
      </ScrollView>
      

      <View style={styles.timerRow}>
        <Text style={styles.selectorTitle}>Timer (s)</Text>
        <View style={styles.timerControls}>
          <Button title="-" onPress={() => setTimerSeconds((s) => Math.max(1, parseFloat((s - 0.5).toFixed(1))))} />
          <Text style={styles.timerValue}>{timerSeconds.toFixed(1)}</Text>
          <Button title="+" onPress={() => setTimerSeconds((s) => Math.min(15, parseFloat((s + 0.5).toFixed(1))))} />
        </View>
      </View>
      {countdown > 0 && <Text>Alternar para o jogo em: {countdown.toFixed(1)}s</Text>}
      <Pressable onPress={startAutomationAction} disabled={loading} style={[styles.primaryActionButton, loading && { opacity: 0.6 }]}> 
        <Text style={styles.primaryActionText}>Iniciar Ação: {actionName}</Text>
      </Pressable>
      
      {loading && <ActivityIndicator size="large" color="#0000ff" style={styles.loadingIndicator} />}
      {loading && (
        <View style={styles.progressBarContainer}>
          <View style={[styles.progressBar, { width: `${progress}%` }]} />
        </View>
      )}
      
      {apiResponse && (
        <View style={styles.responseContainer}>
          <Text style={styles.responseText}>Resposta da API:</Text>
          {apiResponse.logs ? (
            <ScrollView style={styles.logsContainer}>
              {apiResponse.logs.map((log, index) => (
                <Text key={index} style={styles.logText}>{log}</Text>
              ))}
            </ScrollView>
          ) : (
            <Text>{JSON.stringify(apiResponse, null, 2)}</Text>
          )}
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
  input: {
    height: 40,
    borderColor: 'gray',
    borderWidth: 1,
    width: '80%',
    marginBottom: 10,
    paddingHorizontal: 10,
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
  logsContainer: {
    height: 200, // Altura fixa para a área de logs
    borderColor: '#eee',
    borderWidth: 1,
    padding: 5,
    marginTop: 10,
  },
  logText: {
    fontSize: 12,
    color: '#333',
  },
  selectorHeader: {
    width: '100%',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: 10,
  },
  selectorTitle: {
    fontSize: 16,
    fontWeight: 'bold',
  },
  selectorList: {
    width: '100%',
    maxHeight: 120,
    borderWidth: 1,
    borderColor: '#ddd',
    marginVertical: 8,
  },
  selectorItem: {
    padding: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  selectorItemActive: {
    backgroundColor: '#eef',
  },
  selectorItemText: {
    fontSize: 14,
  },
  timerRow: {
    width: '100%',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginVertical: 8,
  },
  timerRow: {
    width: '100%',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginVertical: 8,
  },
  timerControls: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  timerValue: {
    width: 60,
    textAlign: 'center',
    fontSize: 16,
  },
  primaryActionButton: {
    width: '100%',
    backgroundColor: '#1E90FF',
    paddingVertical: 18,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 12,
  },
  primaryActionText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});
