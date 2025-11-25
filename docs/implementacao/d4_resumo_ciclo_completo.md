# 🎉 UTILITÁRIO DE CICLO COMPLETO - CRIADO COM SUCESSO!

## 📋 O Que Foi Criado

### 1. Script Principal: `ciclo_completo_todas_contas.py`
**Localização:** `backend/utils/ciclo_completo_todas_contas.py`

**Funcionalidade:**
- Executa o ciclo completo para **todas as 10 contas** automaticamente
- Fluxo por conta:
  1. Login na conta
  2. Pegar baús
  3. Pegar recursos
  4. Logout
  5. Próxima conta

**Características:**
- ✅ Tratamento robusto de erros
- ✅ Continua mesmo se uma conta falhar
- ✅ Logs detalhados e coloridos
- ✅ Resumo final com estatísticas
- ✅ Interrupção segura (Ctrl+C)
- ✅ Carrega device ID do .env
- ✅ Delays configuráveis

### 2. Script de Teste: `teste_ciclo_uma_conta.py`
**Localização:** `backend/utils/teste_ciclo_uma_conta.py`

**Funcionalidade:**
- Testa o ciclo completo em **apenas UMA conta**
- Útil para validar antes de executar em todas
- Permite escolher qual conta testar

**Como usar:**
```python
# Edite a linha:
CONTA_TESTE_INDEX = 0  # 0=gled, 1=inf, 2=cav, etc.
```

### 3. Documentação: `GUIA_CICLO_COMPLETO.md`
**Localização:** `GUIA_CICLO_COMPLETO.md`

**Conteúdo:**
- Instruções completas de uso
- Configurações disponíveis
- Solução de problemas
- Dicas e melhores práticas
- Exemplos de saída

---

## 🚀 COMO USAR

### Passo 1: Testar com Uma Conta (Recomendado)

```bash
cd c:\Users\gledston.carneiro\TRAE\auto-touch-droid
python backend/utils/teste_ciclo_uma_conta.py
```

**O que vai acontecer:**
1. Script pergunta se deseja continuar
2. Executa o ciclo completo na primeira conta (login_gled)
3. Mostra resumo do teste

**Se funcionar bem, vá para o Passo 2!**

### Passo 2: Executar em Todas as Contas

```bash
cd c:\Users\gledston.carneiro\TRAE\auto-touch-droid
python backend/utils/ciclo_completo_todas_contas.py
```

**O que vai acontecer:**
1. Carrega todas as 10 contas
2. Executa o ciclo completo para cada uma
3. Mostra progresso em tempo real
4. Apresenta resumo final

---

## 📊 Contas Processadas (em ordem)

1. **login_gled** - Template: 02_login_gled.png
2. **login_inf** - Template: 03_login_inf.png
3. **login_cav** - Template: 04_login_cav.png
4. **login_c52** - Template: 05_login_c52.png
5. **login_c53** - Template: 06_login_c53.png
6. **login_c54** - Template: 07_login_c54.png
7. **login_c55** - Template: 08_login_c55.png
8. **login_c56** - Template: 09_login_c56.png
9. **login_c57** - Template: 10_login_c57.png
10. **login_c58** - Template: 11_login_c58.png

---

## ⚙️ Configurações

### Device ID
Configure no arquivo `.env`:
```env
DEFAULT_DEVICE_ID=RXCTB03EXVK
```

### Delays (editáveis no código)
```python
DELAY_APOS_LOGIN = 3        # Após login bem-sucedido
DELAY_ENTRE_ACOES = 2       # Entre pegar baú e recursos
DELAY_APOS_LOGOUT = 5       # Após logout, antes da próxima conta
DELAY_APOS_FALHA = 5        # Após falha, antes de continuar
```

---

## 🎯 Fluxo de Execução

```
┌─────────────────────────────────────────────┐
│  INÍCIO - Carregar configurações            │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  Carregar sequências (login/logout)         │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  LOOP: Para cada conta (1 a 10)             │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  1. LOGIN            │
        └──────────┬───────────┘
                   │
                   ├─── Sucesso ──┐
                   │              │
                   │              ▼
                   │    ┌──────────────────────┐
                   │    │  2. PEGAR BAÚS       │
                   │    └──────────┬───────────┘
                   │              │
                   │              ▼
                   │    ┌──────────────────────┐
                   │    │  3. PEGAR RECURSOS   │
                   │    └──────────┬───────────┘
                   │              │
                   │              ▼
                   │    ┌──────────────────────┐
                   │    │  4. LOGOUT           │
                   │    └──────────┬───────────┘
                   │              │
                   ├─── Falha ────┤
                   │              │
                   ▼              ▼
        ┌──────────────────────────────┐
        │  Próxima conta (ou fim)      │
        └──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  RESUMO FINAL - Estatísticas                │
└─────────────────────────────────────────────┘
```

---

## ⏱️ Tempo Estimado

### Por Conta
- Login: ~10-15s
- Pegar baús: ~5-10s
- Pegar recursos: ~5-10s
- Logout: ~5-10s
- **Total por conta:** ~30-60s

### Todas as Contas
- **10 contas:** ~5-10 minutos
- Varia conforme velocidade do celular e quantidade de itens

---

## 🛡️ Tratamento de Erros

### Se o login falhar:
- ❌ Pula baús e recursos
- ❌ Não tenta logout
- ✅ Continua para próxima conta

### Se baú ou recursos falharem:
- ⚠️ Registra o erro
- ✅ Continua com próximas ações
- ✅ Tenta logout normalmente

### Se logout falhar:
- ⚠️ Registra o erro
- ✅ Continua para próxima conta
- ⚠️ Próximo login pode corrigir o estado

---

## 📝 Exemplo de Saída

```
============================================================
  🚀 CICLO COMPLETO - TODAS AS CONTAS
============================================================
📱 Device ID: RXCTB03EXVK
👥 Total de contas: 10
⏰ Início da execução: 2025-11-24 15:45:00

📂 Carregando sequências de ações...
✅ Sequência de login carregada (11 passos)
✅ Sequência de logout carregada (5 passos)
✅ Ação 'pegar_bau' encontrada
✅ Ação 'pegar_recursos' encontrada

============================================================
  🔄 INICIANDO EXECUÇÃO DO CICLO
============================================================

============================================================
  CONTA 1/10: login_gled
============================================================
⏰ Início: 15:45:05

[1/4] LOGIN - login_gled
✅ Login bem-sucedido: login_gled

[2/4] PEGAR BAÚS - login_gled
✅ Baús coletados: login_gled

[3/4] PEGAR RECURSOS - login_gled
✅ Recursos coletados: login_gled

[4/4] LOGOUT - login_gled
✅ Logout bem-sucedido: login_gled

⏱️ Tempo total para login_gled: 45.3s
⏰ Término: 15:45:50

[... continua para as outras 9 contas ...]

============================================================
  📊 RESUMO FINAL
============================================================
✅ Contas processadas com sucesso: 10
❌ Contas com falha: 0
📊 Total de contas: 10
⏱️ Tempo total de execução: 450.5s (7.5 min)
⏰ Término: 2025-11-24 15:52:30

🎉 TODAS AS CONTAS FORAM PROCESSADAS COM SUCESSO!
============================================================
```

---

## 🔧 Personalização

### Testar Apenas Algumas Contas
Edite `backend/config/accounts_config.py`:
```python
# Teste com 3 contas
accounts = [
    {"name": "login_gled"},
    {"name": "login_inf"},
    {"name": "login_cav"},
]
```

### Mudar Ordem das Contas
Reorganize a lista em `accounts_config.py`

### Pular Ações Específicas
Comente as linhas no script:
```python
# # Executar pegar_bau
# bau_success = execultar_acoes(...)
```

---

## 📞 Solução de Problemas

### "device not found"
```bash
adb kill-server
adb start-server
adb devices
```

### "Sequência não carregada"
Verifique se existem:
- `backend/actions/templates/fazer_login/sequence.json`
- `backend/actions/templates/fazer_logout/sequence.json`

### "Ação não encontrada"
Verifique se existem as pastas:
- `backend/actions/templates/pegar_bau/`
- `backend/actions/templates/pegar_recursos/`

### Templates não detectados
- Ajuste o threshold em `.env`: `DETECTION_THRESHOLD=0.7`
- Recrie os templates com melhor qualidade
- Verifique se a tela do jogo está na mesma resolução

---

## 💡 Dicas Importantes

1. **Primeira vez:** Execute `teste_ciclo_uma_conta.py` primeiro
2. **Celular:** Mantenha desbloqueado e não use durante execução
3. **Bateria:** Mantenha acima de 20%
4. **USB:** Use cabo de qualidade e porta USB estável
5. **Jogo:** Certifique-se de estar na tela inicial antes de começar

---

## 📚 Arquivos Relacionados

- `ciclo_completo_todas_contas.py` - Script principal
- `teste_ciclo_uma_conta.py` - Script de teste
- `GUIA_CICLO_COMPLETO.md` - Documentação completa
- `accounts_config.py` - Configuração de contas
- `.env` - Configurações de ambiente

---

## 🎊 Pronto para Usar!

Você agora tem um sistema completo de automação que:
- ✅ Processa 10 contas automaticamente
- ✅ Coleta baús e recursos de todas
- ✅ Trata erros de forma inteligente
- ✅ Fornece feedback detalhado
- ✅ Pode ser executado periodicamente

**Comece testando com uma conta e depois execute em todas!**

---

**Boa automação! 🚀**

*Criado em: 24/11/2025*  
*Parceria: Claude-Gled Permanent Partnership* ✨
