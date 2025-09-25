import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  SafeAreaView,
  ScrollView,
} from 'react-native';

export default function MainScreen() {
  const [overlayActive, setOverlayActive] = useState(true);
  const [serverStatus, setServerStatus] = useState('Desconectado');

  useEffect(() => {
    // Simula verificação de status
    setTimeout(() => {
      setServerStatus('Aguardando Python Backend...');
    }, 1000);
  }, []);

  const showInstructions = () => {
    Alert.alert(
      'Como Usar o Visual Game Assistant',
      '1. Abra o League of Kingdoms\n' +
      '2. Os controles aparecerão automaticamente sobre o jogo\n' +
      '3. Use o botão ☰ para abrir o menu de ações\n' +
      '4. Toque em qualquer ação para executá-la\n' +
      '5. Use 🛑 para parar emergencialmente\n\n' +
      'O overlay é transparente e não interfere no jogo!',
      [{ text: 'Entendi!' }]
    );
  };

  const renderTemplateGroup = (group) => (
    <TouchableOpacity
      key={group.name}
      style={styles.templateCard}
      onPress={() => startDetection(group)}
      disabled={isDetecting}
    >
      <View style={styles.cardHeader}>
        <Text style={styles.cardTitle}>{group.displayName}</Text>
        <Text style={styles.cardSubtitle}>
          {group.templates.length} templates
        </Text>
      </View>
      <Text style={styles.cardDescription}>
        Detectar elementos de: {group.name}
      </Text>
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>🎮 Visual Game Assistant</Text>
        <Text style={styles.subtitle}>Overlay Transparente para League of Kingdoms</Text>
      </View>

      <ScrollView style={styles.content}>
        {/* Status do Sistema */}
        <View style={styles.statusCard}>
          <Text style={styles.cardTitle}>📊 Status do Sistema</Text>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>Overlay:</Text>
            <Text style={[styles.statusValue, { color: overlayActive ? '#4CAF50' : '#F44336' }]}>
              {overlayActive ? '✅ Ativo' : '❌ Inativo'}
            </Text>
          </View>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>Backend Python:</Text>
            <Text style={[styles.statusValue, { color: '#FF9800' }]}>
              🟡 {serverStatus}
            </Text>
          </View>
        </View>

        {/* Instruções */}
        <View style={styles.instructionsCard}>
          <Text style={styles.cardTitle}>📖 Como Usar</Text>
          <TouchableOpacity style={styles.instructionButton} onPress={showInstructions}>
            <Text style={styles.instructionButtonText}>Ver Instruções Completas</Text>
          </TouchableOpacity>
          
          <View style={styles.quickSteps}>
            <Text style={styles.stepText}>1. Abra o League of Kingdoms</Text>
            <Text style={styles.stepText}>2. Use os controles transparentes</Text>
            <Text style={styles.stepText}>3. Execute ações automaticamente</Text>
          </View>
        </View>

        {/* Ações Disponíveis */}
        <View style={styles.actionsCard}>
          <Text style={styles.cardTitle}>⚡ Ações Disponíveis</Text>
          <Text style={styles.actionsInfo}>
            As ações são carregadas dinamicamente da pasta 'acoes/'.
            Use o overlay transparente para acessá-las durante o jogo.
          </Text>
        </View>

        {/* Aviso Importante */}
        <View style={styles.warningCard}>
          <Text style={styles.warningTitle}>⚠️ Importante</Text>
          <Text style={styles.warningText}>
            Este app funciona como overlay transparente. 
            Minimize esta tela e abra o League of Kingdoms para usar os controles!
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
  },
  header: {
    padding: 20,
    backgroundColor: '#2d2d2d',
    borderBottomWidth: 1,
    borderBottomColor: '#444',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#ccc',
    textAlign: 'center',
    marginTop: 5,
  },
  content: {
    flex: 1,
    padding: 20,
  },
  statusCard: {
    backgroundColor: '#2d2d2d',
    borderRadius: 10,
    padding: 15,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#444',
  },
  instructionsCard: {
    backgroundColor: '#2d2d2d',
    borderRadius: 10,
    padding: 15,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#444',
  },
  actionsCard: {
    backgroundColor: '#2d2d2d',
    borderRadius: 10,
    padding: 15,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#444',
  },
  warningCard: {
    backgroundColor: '#3d2d1d',
    borderRadius: 10,
    padding: 15,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: '#664',
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 10,
  },
  statusRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  statusLabel: {
    fontSize: 14,
    color: '#ccc',
  },
  statusValue: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  instructionButton: {
    backgroundColor: '#4CAF50',
    borderRadius: 8,
    padding: 12,
    marginBottom: 15,
  },
  instructionButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  quickSteps: {
    marginTop: 10,
  },
  stepText: {
    fontSize: 14,
    color: '#ccc',
    marginBottom: 5,
  },
  actionsInfo: {
    fontSize: 14,
    color: '#ccc',
    lineHeight: 20,
  },
  warningTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#FFB74D',
    marginBottom: 8,
  },
  warningText: {
    fontSize: 14,
    color: '#FFE0B2',
    lineHeight: 20,
  },
});