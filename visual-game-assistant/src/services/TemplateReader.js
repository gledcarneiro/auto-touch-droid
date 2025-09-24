import * as FileSystem from 'expo-file-system';

class TemplateReader {
  constructor() {
    // Caminho para a pasta acoes do projeto Python
    this.acoesPath = FileSystem.documentDirectory + '../acoes/';
  }

  /**
   * Carrega todos os templates disponíveis
   */
  async loadAllTemplates() {
    try {
      const templateGroups = [];
      
      // Grupos de templates conhecidos (baseado na estrutura atual)
      const knownGroups = [
        { name: 'fazer_login', displayName: 'Fazer Login' },
        { name: 'fazer_logout', displayName: 'Fazer Logout' },
        { name: 'pegar_bau', displayName: 'Pegar Baú' },
        { name: 'pegar_recursos', displayName: 'Pegar Recursos' },
      ];

      for (const group of knownGroups) {
        const templates = await this.loadTemplateGroup(group.name);
        if (templates.length > 0) {
          templateGroups.push({
            ...group,
            templates,
          });
        }
      }

      return templateGroups;
    } catch (error) {
      console.error('Error loading templates:', error);
      return [];
    }
  }

  /**
   * Carrega templates de um grupo específico
   */
  async loadTemplateGroup(groupName) {
    try {
      const templates = [];
      
      // Simula a leitura dos templates (em produção, isso seria feito via FileSystem)
      // Por enquanto, vamos usar dados mockados baseados na estrutura real
      const mockTemplates = this.getMockTemplates(groupName);
      
      return mockTemplates;
    } catch (error) {
      console.error(`Error loading template group ${groupName}:`, error);
      return [];
    }
  }

  /**
   * Carrega a sequência JSON de um grupo
   */
  async loadSequence(groupName) {
    try {
      // Em produção, isso leria o arquivo sequence.json
      const mockSequence = this.getMockSequence(groupName);
      return mockSequence;
    } catch (error) {
      console.error(`Error loading sequence for ${groupName}:`, error);
      return null;
    }
  }

  /**
   * Dados mockados baseados na estrutura real do projeto Python
   */
  getMockTemplates(groupName) {
    const templateData = {
      fazer_login: [
        { name: '01_google.png', path: '../acoes/fazer_login/01_google.png' },
        { name: '02_login_gled.png', path: '../acoes/fazer_login/02_login_gled.png' },
        { name: '03_login_inf.png', path: '../acoes/fazer_login/03_login_inf.png' },
        { name: '04_login_cav.png', path: '../acoes/fazer_login/04_login_cav.png' },
        { name: '05_login_c52.png', path: '../acoes/fazer_login/05_login_c52.png' },
      ],
      fazer_logout: [
        { name: 'template_step_01.png', path: '../acoes/fazer_logout/template_step_01.png' },
        { name: 'template_step_02.png', path: '../acoes/fazer_logout/template_step_02.png' },
        { name: 'template_step_03.png', path: '../acoes/fazer_logout/template_step_03.png' },
      ],
      pegar_bau: [
        { name: 'template_step_01.png', path: '../acoes/pegar_bau/template_step_01.png' },
        { name: 'template_step_02.png', path: '../acoes/pegar_bau/template_step_02.png' },
        { name: 'template_step_03.png', path: '../acoes/pegar_bau/template_step_03.png' },
        { name: 'template_step_04.png', path: '../acoes/pegar_bau/template_step_04.png' },
      ],
      pegar_recursos: [
        { name: 'template_step_01.png', path: '../acoes/pegar_recursos/template_step_01.png' },
        { name: 'template_step_02.png', path: '../acoes/pegar_recursos/template_step_02.png' },
        { name: 'template_step_03.png', path: '../acoes/pegar_recursos/template_step_03.png' },
        { name: 'template_step_04.png', path: '../acoes/pegar_recursos/template_step_04.png' },
        { name: 'template_step_05.png', path: '../acoes/pegar_recursos/template_step_05.png' },
      ],
    };

    return templateData[groupName] || [];
  }

  /**
   * Dados mockados das sequências
   */
  getMockSequence(groupName) {
    // Baseado na estrutura real do sequence.json do projeto Python
    const sequences = {
      fazer_login: {
        steps: [
          {
            template: '01_google.png',
            action: 'click',
            delay_after: 2000,
            max_attempts: 3,
          },
          {
            template: '02_login_gled.png',
            action: 'click',
            delay_after: 1000,
            max_attempts: 3,
          },
        ],
      },
      fazer_logout: {
        steps: [
          {
            template: 'template_step_01.png',
            action: 'click',
            delay_after: 1000,
            max_attempts: 3,
          },
        ],
      },
    };

    return sequences[groupName] || null;
  }

  /**
   * Método para futura implementação real de leitura de arquivos
   */
  async readRealTemplates() {
    // TODO: Implementar leitura real dos arquivos quando o app estiver rodando no dispositivo
    // Isso requerirá configuração de permissões e acesso ao sistema de arquivos
    try {
      const acoesInfo = await FileSystem.getInfoAsync(this.acoesPath);
      if (acoesInfo.exists && acoesInfo.isDirectory) {
        const contents = await FileSystem.readDirectoryAsync(this.acoesPath);
        return contents;
      }
    } catch (error) {
      console.error('Error reading real templates:', error);
    }
    return [];
  }
}

export default new TemplateReader();