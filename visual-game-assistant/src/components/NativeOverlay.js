import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Dimensions,
  Animated,
  AppState,
} from 'react-native';
import DrawOverlay from '@vokhuyet/react-native-draw-overlay';
import ActionService from '../services/ActionService';

const { width: screenWidth, height: screenHeight } = Dimensions.get('window');

const NativeOverlay = () => {
  const [hasPermission, setHasPermission] = useState(false);
  const [isOverlayActive, setIsOverlayActive] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [actions, setActions] = useState([]);
  const [serverStatus, setServerStatus] = useState(false);
  const [gameDetected, setGameDetected] = useState(false);
  const [slideAnim] = useState(new Animated.Value(-screenWidth * 0.5));

  useEffect(() => {
    checkPermissions();
    loadActions();
    checkServerStatus();
  }, []);

  // Verificar permissão de overlay real
  const checkPermissions = async () => {
    try {
      const permission = await DrawOverlay.checkPermission();
      setHasPermission(permission);
      
      if (!permission) {
        Alert.alert(
          'Permissão Necessária',
          'Para funcionar sobre outros apps, precisamos da permissão "Exibir sobre outros apps".',
          [
            { text: 'Cancelar', style: 'cancel' },
            { text: 'Conceder', onPress: requestPermission }
          ]
        );
      }
    } catch (error) {
      console.error('Erro ao verificar permissões:', error);
    }
  };

  // Solicitar permissão de overlay real
  const requestPermission = async () => {
    try {
      await DrawOverlay.requestPermission();
      const permission = await DrawOverlay.checkPermission();
      setHasPermission(permission);
      
      if (permission) {
        Alert.alert('Sucesso!', 'Permissão concedida! Agora você pode ativar o overlay.');
      }
    } catch (error) {
      console.error('Erro ao solicitar permissão:', error);
      Alert.alert('Erro', 'Não foi possível obter a permissão de overlay.');
    }
  };

  const loadActions = async () => {
    const availableActions = await ActionService.loadAvailableActions();
    setActions(availableActions);
  };

  const checkServerStatus = async () => {
    const status = await ActionService.checkServerStatus();
    setServerStatus(status);
  };

  const toggleOverlay = async () => {
    if (!hasPermission) {
      Alert.alert(
        'Permissão Necessária',
        'Primeiro conceda a permissão "Exibir sobre outros apps".',
        [{ text: 'OK', onPress: checkPermissions }]
      );
      return;
    }

    if (!isOverlayActive) {
      try {
        // Criar overlay com controles flutuantes
        const overlayConfig = {
          width: 300,
          height: 200,
          x: 50,
          y: 100,
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          borderRadius: 10,
        };

        await DrawOverlay.show(overlayConfig, renderOverlayContent());
        setIsOverlayActive(true);
        
        Alert.alert(
          'Overlay Ativado!',
          'Agora minimize este app e abra o League of Kingdoms. Os controles aparecerão sobre o jogo!',
          [{ text: 'Entendi!' }]
        );
      } catch (error) {
        console.error('Erro ao ativar overlay:', error);
        Alert.alert('Erro', 'Falha ao ativar overlay.');
      }
    } else {
      try {
        await DrawOverlay.hide();
        setIsOverlayActive(false);
      } catch (error) {
        console.error('Erro ao desativar overlay:', error);
        setIsOverlayActive(false);
      }
    }
  };

  // Renderizar conteúdo do overlay
  const renderOverlayContent = () => {
    return `
      <div style="
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: white;
        font-family: Arial, sans-serif;
      ">
        <h3>League Assistant</h3>
        <button onclick="executeAction('login')" style="
          margin: 5px;
          padding: 10px 20px;
          background: #4CAF50;
          color: white;
          border: none;
          border-radius: 5px;
          cursor: pointer;
        ">Login</button>
        <button onclick="executeAction('collect')" style="
          margin: 5px;
          padding: 10px 20px;
          background: #2196F3;
          color: white;
          border: none;
          border-radius: 5px;
          cursor: pointer;
        ">Coletar</button>
        <button onclick="executeAction('close')" style="
          margin: 5px;
          padding: 10px 20px;
          background: #f44336;
          color: white;
          border: none;
          border-radius: 5px;
          cursor: pointer;
        ">Fechar</button>
      </div>
      <script>
        function executeAction(action) {
          if (action === 'close') {
            window.ReactNativeWebView.postMessage('close_overlay');
          } else {
            window.ReactNativeWebView.postMessage('action:' + action);
          }
        }
      </script>
    `;
  };

  const toggleMenu = () => {
    const toValue = isMenuOpen ? -screenWidth * 0.5 : 0;
    
    Animated.timing(slideAnim, {
      toValue,
      duration: 250,
      useNativeDriver: true,
    }).start();
    
    setIsMenuOpen(!isMenuOpen);
  };

  const executeAction = async (actionName) => {
    try {
      const result = await ActionService.executeAction(actionName);
      if (result.success) {
        Alert.alert('Sucesso!', `Ação "${actionName}" executada com sucesso!`);
      } else {
        Alert.alert('Erro', result.message || 'Falha ao executar ação');
      }
    } catch (error) {
      Alert.alert('Erro', 'Servidor Python não conectado');
    }
    
    // Fechar menu após executar ação
    if (isMenuOpen) {
      toggleMenu();
    }
  };

  const emergencyStop = async () => {
    try {
      await ActionService.emergencyStop();
      Alert.alert('Parada de Emergência', 'Todas as ações foram interrompidas!');
    } catch (error) {
      Alert.alert('Erro', 'Falha na parada de emergência');
    }
  };

  if (!isOverlayActive) {
    return (
      <View style={styles.setupContainer}>
        <View style={styles.setupCard}>
          <Text style={styles.setupTitle}>🎮 Overlay Nativo</Text>
          <Text style={styles.setupDescription}>
            Este é um overlay REAL que funciona sobre outros apps!
          </Text>
          
          <View style={styles.statusContainer}>
            <View style={styles.statusItem}>
              <Text style={styles.statusLabel}>Permissão Overlay:</Text>
              <Text style={[styles.statusValue, { color: hasPermission ? '#4CAF50' : '#F44336' }]}>
                {hasPermission ? '✅ Concedida' : '❌ Negada'}
              </Text>
            </View>
            
            <View style={styles.statusItem}>
              <Text style={styles.statusLabel}>Servidor Python:</Text>
              <Text style={[styles.statusValue, { color: serverStatus ? '#4CAF50' : '#F44336' }]}>
                {serverStatus ? '✅ Conectado' : '❌ Desconectado'}
              </Text>
            </View>
          </View>

          <TouchableOpacity 
            style={[styles.activateButton, !hasPermission && styles.disabledButton]} 
            onPress={toggleOverlay}
            disabled={!hasPermission}
          >
            <Text style={styles.activateButtonText}>
              {hasPermission ? '🚀 Ativar Overlay' : '🔒 Conceder Permissão'}
            </Text>
          </TouchableOpacity>

          {!hasPermission && (
            <TouchableOpacity style={styles.permissionButton} onPress={requestPermission}>
              <Text style={styles.permissionButtonText}>⚙️ Solicitar Permissão</Text>
            </TouchableOpacity>
          )}

          <Text style={styles.instructions}>
            💡 Após ativar, minimize este app e abra o League of Kingdoms. 
            Os controles aparecerão sobre o jogo!
          </Text>
        </View>
      </View>
    );
  }

  // Overlay ativo - renderizar controles flutuantes
  return (
    <View style={styles.overlay} pointerEvents="box-none">
      {/* Controles Superiores */}
      <View style={styles.topControls}>
        <TouchableOpacity style={[styles.controlButton, styles.triggerButton]} onPress={toggleMenu}>
          <Text style={styles.controlIcon}>☰</Text>
        </TouchableOpacity>
        
        <TouchableOpacity style={[styles.controlButton, styles.emergencyButton]} onPress={emergencyStop}>
          <Text style={styles.controlIcon}>⏹</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.controlButton, styles.statusButton, { backgroundColor: serverStatus ? 'rgba(76, 175, 80, 0.9)' : 'rgba(244, 67, 54, 0.9)' }]} 
          onPress={checkServerStatus}
        >
          <Text style={styles.controlIcon}>●</Text>
        </TouchableOpacity>

        <TouchableOpacity style={[styles.controlButton, styles.closeButton]} onPress={toggleOverlay}>
          <Text style={styles.controlIcon}>✕</Text>
        </TouchableOpacity>
      </View>

      {/* Menu Retrátil */}
      <Animated.View style={[styles.menu, { transform: [{ translateX: slideAnim }] }]}>
        <View style={styles.menuHeader}>
          <Text style={styles.menuTitle}>🎮 Ações Disponíveis</Text>
          <TouchableOpacity onPress={toggleMenu}>
            <Text style={styles.closeMenuButton}>✕</Text>
          </TouchableOpacity>
        </View>
        
        <View style={styles.actionsList}>
          {actions.map((action, index) => (
            <TouchableOpacity
              key={index}
              style={styles.actionButton}
              onPress={() => executeAction(action.name)}
            >
              <Text style={styles.actionIcon}>{action.icon}</Text>
              <Text style={styles.actionText}>{action.displayName}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </Animated.View>
    </View>
  );
};

const styles = StyleSheet.create({
  // Estilos de configuração
  setupContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#1a1a1a',
    padding: 20,
  },
  
  setupCard: {
    backgroundColor: '#2d2d2d',
    borderRadius: 15,
    padding: 25,
    width: '100%',
    maxWidth: 400,
    alignItems: 'center',
  },
  
  setupTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 10,
    textAlign: 'center',
  },
  
  setupDescription: {
    fontSize: 16,
    color: '#ccc',
    textAlign: 'center',
    marginBottom: 20,
  },
  
  statusContainer: {
    width: '100%',
    marginBottom: 20,
  },
  
  statusItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 10,
  },
  
  statusLabel: {
    color: '#ccc',
    fontSize: 14,
  },
  
  statusValue: {
    fontSize: 14,
    fontWeight: 'bold',
  },
  
  activateButton: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
    marginBottom: 10,
  },
  
  disabledButton: {
    backgroundColor: '#666',
  },
  
  activateButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  
  permissionButton: {
    backgroundColor: '#2196F3',
    paddingHorizontal: 25,
    paddingVertical: 12,
    borderRadius: 20,
    marginBottom: 15,
  },
  
  permissionButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  
  instructions: {
    fontSize: 12,
    color: '#999',
    textAlign: 'center',
    lineHeight: 18,
  },

  // Estilos do overlay
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'transparent',
  },
  
  topControls: {
    position: 'absolute',
    top: 40,
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
    backgroundColor: 'rgba(0, 150, 255, 0.9)',
  },
  
  emergencyButton: {
    backgroundColor: 'rgba(255, 50, 50, 0.9)',
  },
  
  statusButton: {
    backgroundColor: 'rgba(50, 50, 50, 0.9)',
  },
  
  closeButton: {
    backgroundColor: 'rgba(100, 100, 100, 0.9)',
  },
  
  controlIcon: {
    fontSize: 20,
    color: '#fff',
    fontWeight: 'bold',
  },
  
  menu: {
    position: 'absolute',
    top: 100,
    left: 0,
    width: screenWidth * 0.5,
    height: screenHeight - 100,
    backgroundColor: 'rgba(30, 30, 30, 0.95)',
    borderTopRightRadius: 15,
    borderBottomRightRadius: 15,
    elevation: 10,
  },
  
  menuHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.1)',
  },
  
  menuTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  
  closeMenuButton: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  
  actionsList: {
    flex: 1,
    padding: 10,
  },
  
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
  },
  
  actionIcon: {
    fontSize: 20,
    marginRight: 10,
  },
  
  actionText: {
    color: '#fff',
    fontSize: 14,
    flex: 1,
  },
});

export default NativeOverlay;