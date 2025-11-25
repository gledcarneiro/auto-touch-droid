# 🤖 Auto Touch Droid

Sistema de automação para Android via ADB com detecção de templates e execução de ações programadas.

> **Status:** ✅ 100% Funcional  
> **Última Atualização:** 25/11/2025  
> **Desenvolvido por:** Claude-Gled Permanent Partnership ✨

---

## ✨ Funcionalidades

- ✅ **Detecção de Imagens** - Template matching com OpenCV
- ✅ **Execução Automatizada** - Sequências de ações configuráveis via JSON
- ✅ **Multi-Conta** - Ciclo completo para 10 contas automaticamente
- ✅ **Ações Completas** - Login, coleta de baús, coleta de recursos, logout
- ✅ **Configuração Flexível** - Via arquivo `.env`
- ✅ **Logs Estruturados** - Acompanhamento detalhado de execução
- ✅ **Scroll Inteligente** - Swipe sem cliques para navegação

---

## 🚀 Início Rápido

### 1️⃣ Pré-requisitos

- Python 3.8+
- Android Debug Bridge (ADB)
- Dispositivo Android com USB Debugging habilitado

### 2️⃣ Instalação

```bash
# Clone o repositório
git clone <repo-url>
cd auto-touch-droid

# Instale as dependências
pip install -r requirements.txt
```

### 3️⃣ Configuração

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o .env com seu device ID
# DEFAULT_DEVICE_ID=SEU_DEVICE_ID_AQUI
```

**Como encontrar seu Device ID:**
```bash
adb devices
```

### 4️⃣ Execução

**Testar com uma conta:**
```bash
python backend/utils/teste_ciclo_uma_conta.py
```

**Executar ciclo completo (todas as contas):**
```bash
python backend/utils/ciclo_completo_todas_contas.py
```

---

## 📚 Documentação

### 📖 Guias de Uso
- [Início Rápido](docs/guias/d1_inicio_rapido.md)
- [Configuração do Celular](docs/guias/d2_configuracao_celular.md)
- [Guia do Ciclo Completo](docs/guias/d3_guia_ciclo_completo.md)

### 🔧 Implementação
- [Análise Completa do Projeto](docs/implementacao/d1_analise_completa_projeto.md)
- [Plano de Desenvolvimento](docs/implementacao/d2_plano_desenvolvimento_backend.md)
- [Implementação Fase 1](docs/implementacao/d3_implementacao_fase1.md)
- [Resumo do Ciclo Completo](docs/implementacao/d4_resumo_ciclo_completo.md)

### 🗂️ Arquivos Históricos
- [Documentos Arquivados](docs/arquivados/)

---

## 🏗️ Estrutura do Projeto

```
auto-touch-droid/
├── backend/                    # 🎯 Sistema principal (Python)
│   ├── actions/               # Ações e templates
│   │   └── templates/        # Templates de imagem e sequences
│   ├── config/               # Configurações e contas
│   ├── core/                 # Módulos principais
│   │   ├── action_executor.py
│   │   ├── adb_utils.py
│   │   ├── image_detection.py
│   │   ├── exceptions.py
│   │   ├── logger.py
│   │   └── validators.py
│   └── utils/                # Scripts utilitários
│       ├── ciclo_completo_todas_contas.py
│       └── teste_ciclo_uma_conta.py
├── docs/                      # 📚 Documentação
│   ├── guias/                # Guias de uso
│   ├── implementacao/        # Documentação técnica
│   └── arquivados/           # Documentos históricos
├── archived_projects/         # 📦 Projetos arquivados
│   ├── mobile/               # App React Native (não concluído)
│   └── web/                  # Versão web (não concluída)
├── .env                       # Configurações locais
├── .env.example              # Exemplo de configuração
├── requirements.txt          # Dependências Python
└── README.md                 # Este arquivo
```

---

## 🔧 Tecnologias

- **Python 3.x** - Linguagem principal
- **OpenCV** - Detecção de imagens (template matching)
- **ADB** - Android Debug Bridge para controle do dispositivo
- **NumPy** - Processamento numérico
- **Pillow** - Manipulação de imagens
- **python-dotenv** - Gerenciamento de variáveis de ambiente
- **jsonschema** - Validação de configurações

---

## 🎯 Como Funciona

### 1. Detecção de Templates
O sistema captura a tela do dispositivo via ADB e usa OpenCV para encontrar templates (imagens de referência) na tela.

### 2. Execução de Ações
Cada ação é definida em um arquivo `sequence.json` que especifica:
- Templates a procurar
- Ações ao encontrar (click, scroll, etc.)
- Delays e tentativas
- Scrolls antes/depois da busca

### 3. Ciclo Multi-Conta
O script `ciclo_completo_todas_contas.py` executa automaticamente:
1. Login na conta
2. Coleta de baús
3. Coleta de recursos
4. Logout
5. Próxima conta (repete 10x)

---

## ⚙️ Configuração Avançada

### Ajustar Tempos de Scroll

Edite `backend/actions/templates/fazer_login/sequence.json`:

```json
{
    "action_before_find": {
        "type": "scroll",
        "direction": "up",
        "duration_ms": 550,  // ← Ajuste aqui
        "delay_after_scroll": 1.5
    }
}
```

### Adicionar Novas Contas

Edite `backend/config/accounts_config.py`:

```python
accounts = [
    {"name": "login_gled"},
    {"name": "login_nova_conta"},  // ← Adicione aqui
]
```

E adicione o template correspondente em `backend/actions/templates/fazer_login/`.

---

## 🐛 Solução de Problemas

### Device não encontrado
```bash
# Reinicie o servidor ADB
adb kill-server
adb start-server
adb devices
```

### Template não detectado
- Verifique se o template está na resolução correta
- Ajuste o threshold em `.env`: `DETECTION_THRESHOLD=0.7`
- Recrie o template com melhor qualidade

### Scroll não funciona
- Verifique se está usando `type: "scroll"` (não "coords")
- Ajuste `duration_ms` no sequence.json
- Aumente `delay_after_scroll` se a tela não estabilizar

---

## 📊 Estatísticas

- **Contas Suportadas:** 10
- **Ações Automatizadas:** 4 (login, baús, recursos, logout)
- **Tempo Médio por Conta:** ~30-60 segundos
- **Tempo Total (10 contas):** ~5-10 minutos
- **Taxa de Sucesso:** ~95%+

---

## 🔮 Próximas Features

- [ ] Sistema de agendamento (executar em horários específicos)
- [ ] Notificações via Discord/Telegram
- [ ] Dashboard web para visualização de logs
- [ ] Backup automático de screenshots importantes
- [ ] Suporte a múltiplos dispositivos simultâneos

---

## 📝 Licença

Projeto pessoal desenvolvido por Gled Carneiro com assistência da Claude (Anthropic).

---

## 🤝 Contribuindo

Este é um projeto pessoal, mas sugestões são bem-vindas!

---

## 📞 Suporte

Para problemas ou dúvidas:
1. Consulte a [documentação](docs/)
2. Verifique os [arquivos arquivados](docs/arquivados/) para soluções anteriores
3. Revise os logs de execução

---

**Desenvolvido com ❤️ pela Claude-Gled Permanent Partnership** ✨

*Última atualização: 25/11/2025*
