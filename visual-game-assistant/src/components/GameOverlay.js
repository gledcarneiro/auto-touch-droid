import React, { useState, useRef, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Animated,
  Dimensions,
  ScrollView,
  Alert,
} from 'react-native';
import ActionService from '../services/ActionService';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

export default function GameOverlay() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [actions, setActions] = useState([]);
  const [serverStatus, setServerStatus] = useState(false);
  const slideAnim = useRef(new Animated.Value(-screenWidth * 0.5)).current;

  // Carregar ações ao inicializar
  useEffect(() => {
    loadActions();
    checkServerStatus();
  }, []);

  const loadActions = async () => {
    const availableActions = await ActionService.loadAvailableActions();
    setActions(availableActions);
  };

  const checkServerStatus = async () => {
    const status = await ActionService.checkServerStatus();
    setServerStatus(status);
  };

  const toggleMenu = () => {
    const toValue = isMenuOpen ? -screenWidth * 0.5 : 0;
    
    Animated.timing(slideAnim, {
      toValue,
      duration: 250, // Animação rápida mas suave
      useNativeDriver: true,
    }).start();
    
    setIsMenuOpen(!isMenuOpen);
  };

  const executeAction = async (action) => {
    // Fecha o menu imediatamente
    toggleMenu();
    
    setIsExecuting(true);
    
    try {
      const result = await ActionService.executeAction(action.originalName || action.id);
      
      if (result.success) {
        Alert.alert(
          'Sucesso!',
          `Ação "${action.name}" executada com sucesso!`,
          [{ text: 'OK', onPress: () => setIsExecuting(false) }]
        );
      } else {
        Alert.alert(
          'Aviso',
          result.message || `Simulando execução de: ${action.name}\n\n${result.error || 'Backend Python não conectado'}`,
          [{ text: 'OK', onPress: () => setIsExecuting(false) }]
        );
      }
    } catch (error) {
      Alert.alert('Erro', 'Falha ao executar ação');
      setIsExecuting(false);
    }
  };

  const emergencyStop = async () => {
    Alert.alert(
      'Parada de Emergência',
      'Tem certeza que deseja parar todas as execuções?',
      [
        { text: 'Cancelar', style: 'cancel' },
        { 
          text: 'PARAR TUDO', 
          style: 'destructive',
          onPress: async () => {
            setIsExecuting(false);
            const result = await ActionService.emergencyStop();
            
            if (result.success) {
              Alert.alert('Sucesso', 'Todas as execuções foram interrompidas!');
            } else {
              Alert.alert('Aviso', 'Execuções locais interrompidas.\n\n' + (result.error || 'Backend Python não conectado'));
            }
          }
        }
      ]
    );
  };

  return (
    <View style={styles.overlay} pointerEvents="box-none">
      {/* Controles superiores sempre visíveis */}
      <View style={styles.topControls}>
        <TouchableOpacity 
          style={[styles.controlButton, styles.triggerButton]} 
          onPress={toggleMenu}
        >
          <Text style={styles.controlIcon}>☰</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.controlButton, styles.emergencyButton]} 
          onPress={emergencyStop}
        >
          <Text style={styles.controlIcon}>🛑</Text>
        </TouchableOpacity>
        
        {/* Indicador de Status do Servidor */}
        <TouchableOpacity
          style={[styles.controlButton, styles.statusButton]}
          onPress={checkServerStatus}
        >
          <Text style={styles.controlIcon}>
            {serverStatus ? '🟢' : '🔴'}
          </Text>
        </TouchableOpacity>
        
        {/* Futuros controles */}
        <TouchableOpacity 
          style={[styles.controlButton, styles.futureButton]} 
          disabled
        >
          <Text style={styles.controlIcon}>🔄</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.controlButton, styles.futureButton]} 
          disabled
        >
          <Text style={styles.controlIcon}>⚙️</Text>
        </TouchableOpacity>
      </View>

      {/* Menu Retrátil */}
      <Animated.View 
        style={[
          styles.menu,
          {
            transform: [{ translateX: slideAnim }]
          }
        ]}
      >
        <View style={styles.menuHeader}>
          <Text style={styles.menuTitle}>Ações Disponíveis</Text>
        </View>
        
        <ScrollView style={styles.actionsList} showsVerticalScrollIndicator={false}>
          {actions.map((action) => (
            <TouchableOpacity
              key={action.id}
              style={styles.actionButton}
              onPress={() => executeAction(action)}
              disabled={isExecuting}
            >
              <Text style={styles.actionIcon}>{action.icon}</Text>
              <Text style={styles.actionText}>{action.name}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </Animated.View>

      {/* Overlay de Loading */}
      {isExecuting && (
        <View style={styles.loadingOverlay}>
          <Text style={styles.loadingText}>Executando ação...</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'transparent', // Totalmente transparente
  },
  
  // Barra de Controles Superior
  topControls: {
    position: 'absolute',
    top: 40, // Espaço para status bar
    left: 10,
    flexDirection: 'row',
    zIndex: 1000,
  },
  
  controlButton: {
    width: 50,
    height: 50,
    borderRadius: 25,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 10,
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
  },
  
  triggerButton: {
    backgroundColor: 'rgba(0, 150, 255, 0.9)', // Azul semi-transparente
  },
  
  emergencyButton: {
    backgroundColor: 'rgba(255, 50, 50, 0.9)', // Vermelho semi-transparente
  },
  
  statusButton: {
    backgroundColor: 'rgba(50, 50, 50, 0.9)', // Cinza escuro semi-transparente
  },
  
  futureButton: {
    backgroundColor: 'rgba(100, 100, 100, 0.5)', // Cinza desabilitado
  },
  
  controlIcon: {
    fontSize: 20,
    color: '#fff',
    fontWeight: 'bold',
  },
  
  // Menu Retrátil
  menu: {
    position: 'absolute',
    top: 100, // Abaixo dos controles
    left: 0,
    width: screenWidth * 0.5, // Metade da tela
    height: screenHeight - 100,
    backgroundColor: 'rgba(30, 30, 30, 0.95)', // Quase opaco
    borderTopRightRadius: 15,
    borderBottomRightRadius: 15,
    elevation: 10,
    shadowColor: '#000',
    shadowOffset: { width: 2, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 8,
  },
  
  menuHeader: {
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.1)',
  },
  
  menuTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  
  actionsList: {
    flex: 1,
    padding: 10,
  },
  
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(50, 50, 50, 0.8)',
    borderRadius: 10,
    padding: 15,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  
  actionIcon: {
    fontSize: 20,
    marginRight: 12,
  },
  
  actionText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '500',
    flex: 1,
  },
  
  // Loading Overlay
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 2000,
  },
  
  loadingText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});