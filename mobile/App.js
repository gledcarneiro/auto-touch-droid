import React, { useEffect, useState, useMemo } from 'react';
import { View, Text, TextInput, Pressable, FlatList, ActivityIndicator, SafeAreaView } from 'react-native';

const defaultApi = 'http://localhost:8000';

export default function App() {
  const [apiUrl, setApiUrl] = useState(defaultApi);
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState(null);
  const [resources, setResources] = useState(null);
  const [devices, setDevices] = useState([]);
  const [actions, setActions] = useState([]);
  const [countdown, setCountdown] = useState(3);
  const [runningCountdown, setRunningCountdown] = useState(false);
  const [viability, setViability] = useState(null);

  const headers = useMemo(() => ({ 'Content-Type': 'application/json' }), []);

  const fetchJson = async (path) => {
    const res = await fetch(`${apiUrl}${path}`, { headers });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  };

  const loadAll = async () => {
    setLoading(true);
    try {
      const [h, r, d, a] = await Promise.all([
        fetchJson('/health'),
        fetchJson('/poc/resources'),
        fetchJson('/poc/devices'),
        fetchJson('/poc/actions/list'),
      ]);
      setHealth(h);
      setResources(r);
      setDevices(d.devices || []);
      setActions(a.actions || []);
    } catch (e) {
      setHealth(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
  }, [apiUrl]);

  useEffect(() => {
    let timer;
    if (runningCountdown) {
      timer = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(timer);
            setRunningCountdown(false);
            executeViability();
            return 3;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [runningCountdown]);

  const executeViability = async () => {
    setLoading(true);
    try {
      const v = await fetchJson('/poc/viability');
      setViability(v);
    } catch (e) {
      setViability(null);
    } finally {
      setLoading(false);
    }
  };

  const startAction = () => {
    if (loading) return;
    setViability(null);
    setRunningCountdown(true);
  };

  const renderAction = ({ item }) => (
    <View style={{ padding: 8, borderBottomWidth: 1, borderColor: '#eee' }}>
      <Text style={{ fontWeight: 'bold' }}>{item.group}</Text>
      <Text>{Array.isArray(item.steps) ? `${item.steps.length} passos` : '0 passos'}</Text>
    </View>
  );

  const renderDevice = ({ item }) => (
    <View style={{ padding: 8, borderBottomWidth: 1, borderColor: '#eee' }}>
      <Text style={{ fontWeight: 'bold' }}>{item.name}</Text>
      <Text>{item.id}</Text>
    </View>
  );

  return (
    <SafeAreaView style={{ flex: 1, padding: 16 }}>
      <Text style={{ fontSize: 18, fontWeight: 'bold', marginBottom: 8 }}>Mobile PoC</Text>

      <Text style={{ marginBottom: 4 }}>API URL</Text>
      <TextInput
        value={apiUrl}
        onChangeText={setApiUrl}
        autoCapitalize="none"
        autoCorrect={false}
        style={{ borderWidth: 1, borderColor: '#ccc', padding: 10, borderRadius: 6, marginBottom: 12 }}
      />

      {loading ? <ActivityIndicator /> : (
        <View style={{ marginBottom: 12 }}>
          <Text>Health: {health ? 'ok' : 'erro'}</Text>
          {resources && (
            <Text>Python {resources.python} | cv2 {resources.cv2} | numpy {resources.numpy}</Text>
          )}
        </View>
      )}

      <Text style={{ fontWeight: 'bold', marginTop: 8 }}>Dispositivos</Text>
      <FlatList data={devices} keyExtractor={(i) => i.id} renderItem={renderDevice} style={{ maxHeight: 120 }} />

      <Text style={{ fontWeight: 'bold', marginTop: 8 }}>Ações</Text>
      <FlatList data={actions} keyExtractor={(i) => i.group} renderItem={renderAction} style={{ maxHeight: 200 }} />

      <View style={{ marginTop: 16 }}>
        <Text>Contagem regressiva: {runningCountdown ? countdown : 'pronto'}</Text>
        <Pressable onPress={startAction} disabled={loading} style={{ backgroundColor: '#1E90FF', padding: 16, borderRadius: 8, marginTop: 8 }}>
          <Text style={{ color: '#fff', fontWeight: 'bold', textAlign: 'center' }}>Iniciar Ação</Text>
        </Pressable>
      </View>

      {viability && (
        <View style={{ marginTop: 12 }}>
          <Text style={{ fontWeight: 'bold' }}>Resultado Viability</Text>
          <Text>{JSON.stringify(viability)}</Text>
        </View>
      )}
    </SafeAreaView>
  );
}

