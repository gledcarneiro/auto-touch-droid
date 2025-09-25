import AsyncStorage from '@react-native-async-storage/async-storage';

class ActionService {
  constructor() {
    this.baseUrl = 'http://localhost:8000'; // Servidor Python local
    this.actions = [];
  }

  // Mapear ícones para tipos de ação
  getActionIcon(actionName) {
    const iconMap = {
      'fazer_login': '🔑',
      'fazer_logout': '🚪',
      'pegar_bau': '📦',
      'pegar_recursos': '💎',
      'coletar': '🎯',
      'batalha': '⚔️',
      'construir': '🏗️',
      'upgrade': '⬆️',
    };

    // Busca por palavras-chave no nome da ação
    for (const [key, icon] of Object.entries(iconMap)) {
      if (actionName.toLowerCase().includes(key)) {
        return icon;
      }
    }
    
    return '🎮'; // Ícone padrão
  }

  // Formatar nome da ação para exibição
  formatActionName(actionName) {
    return actionName
      .replace(/_/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase());
  }

  // Carregar ações disponíveis (mockado por enquanto)
  async loadAvailableActions() {
    try {
      // Por enquanto, vamos usar dados mockados
      // Depois vamos fazer uma requisição para o Python listar as pastas em 'acoes/'
      const mockActions = [
        'fazer_login_c52',
        'fazer_login_c53', 
        'fazer_login_c54',
        'fazer_login_c55',
        'fazer_login_c56',
        'fazer_login_c57',
        'fazer_login_c58',
        'pegar_bau',
        'pegar_recursos',
        'fazer_logout'
      ];

      this.actions = mockActions.map(actionName => ({
        id: actionName,
        name: this.formatActionName(actionName),
        icon: this.getActionIcon(actionName),
        originalName: actionName
      }));

      return this.actions;
    } catch (error) {
      console.error('Erro ao carregar ações:', error);
      return [];
    }
  }

  // Executar ação via API Python
  async executeAction(actionId) {
    try {
      const response = await fetch(`${this.baseUrl}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          action: actionId,
          timestamp: new Date().toISOString()
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      return result;
    } catch (error) {
      console.error('Erro ao executar ação:', error);
      
      // Se não conseguir conectar com o Python, simula execução
      return {
        success: false,
        error: 'Não foi possível conectar com o backend Python',
        message: `Ação "${actionId}" seria executada aqui`
      };
    }
  }

  // Parar todas as execuções
  async emergencyStop() {
    try {
      const response = await fetch(`${this.baseUrl}/stop`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Erro ao parar execuções:', error);
      return {
        success: false,
        error: 'Não foi possível conectar com o backend Python'
      };
    }
  }

  // Verificar status do servidor Python
  async checkServerStatus() {
    try {
      const response = await fetch(`${this.baseUrl}/status`, {
        method: 'GET',
        timeout: 3000,
      });

      return response.ok;
    } catch (error) {
      return false;
    }
  }

  // Salvar configurações localmente
  async saveSettings(settings) {
    try {
      await AsyncStorage.setItem('gameAssistantSettings', JSON.stringify(settings));
    } catch (error) {
      console.error('Erro ao salvar configurações:', error);
    }
  }

  // Carregar configurações locais
  async loadSettings() {
    try {
      const settings = await AsyncStorage.getItem('gameAssistantSettings');
      return settings ? JSON.parse(settings) : {};
    } catch (error) {
      console.error('Erro ao carregar configurações:', error);
      return {};
    }
  }
}

// Singleton para usar em toda a aplicação
export default new ActionService();