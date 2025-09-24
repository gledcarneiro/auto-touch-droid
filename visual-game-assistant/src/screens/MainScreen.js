import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function MainScreen() {
  const [isDetecting, setIsDetecting] = useState(false);

  // Templates mockados para teste
  const mockTemplates = [
    {
      name: 'fazer_login',
      displayName: 'Fazer Login',
      description: 'Automatizar processo de login',
      templates: ['01_google.png', '02_login_gled.png']
    },
    {
      name: 'pegar_bau',
      displayName: 'Pegar Baú',
      description: 'Coletar baús automaticamente',
      templates: ['template_step_01.png', 'template_step_02.png']
    },
    {
      name: 'pegar_recursos',
      displayName: 'Pegar Recursos',
      description: 'Coletar recursos do jogo',
      templates: ['template_step_01.png', 'template_step_02.png']
    }
  ];

  const startDetection = async (templateGroup) => {
    setIsDetecting(true);
    
    // Simular detecção
    setTimeout(() => {
      Alert.alert(
        'Teste OK!',
        `Template "${templateGroup.displayName}" selecionado!\n\nEm breve conectaremos com o sistema Python.`
      );
      setIsDetecting(false);
    }, 1000);
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
        <Text style={styles.title}>Visual Game Assistant</Text>
        <Text style={styles.subtitle}>
          Detecção Visual Inteligente
        </Text>
      </View>

      <ScrollView style={styles.content}>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Templates Disponíveis</Text>
          {mockTemplates.map(renderTemplateGroup)}
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Status</Text>
          <View style={styles.statusCard}>
            <Text style={styles.statusText}>
              {isDetecting ? '🔍 Processando...' : '✅ Pronto para detectar'}
            </Text>
          </View>
        </View>
      </ScrollView>

      {isDetecting && (
        <View style={styles.loadingOverlay}>
          <Text style={styles.loadingText}>Detectando...</Text>
        </View>
      )}
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
    borderBottomWidth: 1,
    borderBottomColor: '#333',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 16,
    color: '#888',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  section: {
    marginBottom: 30,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 15,
  },
  templateCard: {
    backgroundColor: '#2a2a2a',
    borderRadius: 10,
    padding: 15,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: '#333',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },
  cardSubtitle: {
    fontSize: 12,
    color: '#888',
  },
  cardDescription: {
    fontSize: 14,
    color: '#ccc',
  },
  emptyState: {
    padding: 40,
    alignItems: 'center',
  },
  emptyText: {
    color: '#888',
    fontSize: 16,
  },
  statusCard: {
    backgroundColor: '#2a2a2a',
    borderRadius: 10,
    padding: 15,
    borderWidth: 1,
    borderColor: '#333',
  },
  statusText: {
    color: '#fff',
    fontSize: 16,
    textAlign: 'center',
  },
  resultCard: {
    backgroundColor: '#2a2a2a',
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#4CAF50',
  },
  resultText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  resultPosition: {
    color: '#888',
    fontSize: 12,
    marginTop: 4,
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});