# Visual Game Assistant

## 📱 Módulo React Native para Detecção Visual

Este é o módulo React Native do projeto **auto-touch-droid**, focado exclusivamente em **detecção visual inteligente** para jogos mobile.

### 🎯 Objetivo

Criar um app Android nativo que detecta elementos visuais na tela usando templates do projeto Python principal, sem realizar ações de toque.

### 🏗️ Arquitetura

```
visual-game-assistant/
├── src/
│   ├── components/          # Componentes reutilizáveis
│   ├── screens/            # Telas do app
│   │   └── MainScreen.js   # Tela principal
│   ├── services/           # Serviços de negócio
│   │   ├── TemplateReader.js    # Leitura de templates
│   │   └── DetectionService.js  # Detecção visual
│   └── utils/              # Utilitários
├── assets/                 # Recursos do app
└── App.js                 # Componente principal
```

### 🔧 Funcionalidades

- ✅ **Interface Moderna**: UI dark theme com React Native
- ✅ **Leitura de Templates**: Acessa templates da pasta `../acoes/`
- ✅ **Detecção Visual**: Simula detecção usando react-native-vision-camera
- ✅ **Resultados em Tempo Real**: Mostra confiança e posição dos elementos
- 🔄 **Monitoramento Contínuo**: Detecção automática em intervalos

### 📦 Dependências

```json
{
  "react-native-vision-camera": "^3.x",
  "expo-file-system": "^15.x",
  "expo-media-library": "^15.x",
  "@react-native-async-storage/async-storage": "^1.x"
}
```

### 🚀 Como Executar

1. **Instalar dependências**:
   ```bash
   npm install
   ```

2. **Executar no Android**:
   ```bash
   npm run android
   ```

3. **Executar no iOS**:
   ```bash
   npm run ios
   ```

4. **Executar no Web** (desenvolvimento):
   ```bash
   npm run web
   ```

### 🔗 Integração com Projeto Python

O app lê templates diretamente da pasta `../acoes/` do projeto Python:

```
auto-touch-droid/
├── acoes/                    # ← Templates compartilhados
│   ├── fazer_login/
│   ├── fazer_logout/
│   ├── pegar_bau/
│   └── pegar_recursos/
└── visual-game-assistant/    # ← Este módulo React Native
```

### 📋 Templates Suportados

- **fazer_login**: Detecção de elementos de login
- **fazer_logout**: Detecção de elementos de logout  
- **pegar_bau**: Detecção de baús no jogo
- **pegar_recursos**: Detecção de recursos coletáveis

### 🎮 Fluxo de Uso

1. **Abrir o app** no dispositivo Android
2. **Selecionar grupo** de templates (ex: "Fazer Login")
3. **Iniciar detecção** - app captura tela e procura templates
4. **Ver resultados** - elementos encontrados com posição e confiança
5. **Repetir** conforme necessário

### 🔮 Roadmap Futuro

- [ ] **OpenCV Integration**: Implementar react-native-opencv
- [ ] **Real File Access**: Leitura real dos templates do projeto Python
- [ ] **Continuous Monitoring**: Detecção automática em background
- [ ] **Notification System**: Alertas quando elementos são detectados
- [ ] **Statistics Dashboard**: Métricas de detecção
- [ ] **Template Editor**: Interface para criar/editar templates

### 🤝 Relação com Projeto Principal

| Projeto Python | React Native Module |
|----------------|-------------------|
| 🎯 Captura & Gravação | 👁️ Detecção Visual |
| 🖱️ Execução de Ações | 📊 Monitoramento |
| 🛠️ Desenvolvimento | 📱 Produção |

### 📱 Publicação

Este módulo pode ser publicado independentemente na **Google Play Store** como um app de detecção visual para jogos.

---

**Desenvolvido como parte do projeto auto-touch-droid** 🚀