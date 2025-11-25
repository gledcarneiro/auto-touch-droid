# 🎮 GUIA DE USO - Ciclo Completo Todas as Contas

## 📋 Descrição

O script `ciclo_completo_todas_contas.py` automatiza o processo de:
1. **Login** em cada conta (da primeira à última)
2. **Pegar baús** disponíveis
3. **Pegar recursos** disponíveis
4. **Logout** da conta
5. **Repetir** para a próxima conta

## 🎯 Contas Processadas

O script processa **10 contas** na seguinte ordem:

1. `login_gled` (02_login_gled.png)
2. `login_inf` (03_login_inf.png)
3. `login_cav` (04_login_cav.png)
4. `login_c52` (05_login_c52.png)
5. `login_c53` (06_login_c53.png)
6. `login_c54` (07_login_c54.png)
7. `login_c55` (08_login_c55.png)
8. `login_c56` (09_login_c56.png)
9. `login_c57` (10_login_c57.png)
10. `login_c58` (11_login_c58.png)

## 🚀 Como Executar

### Método 1: Execução Direta
```bash
cd c:\Users\gledston.carneiro\TRAE\auto-touch-droid
python backend/utils/ciclo_completo_todas_contas.py
```

### Método 2: Via PowerShell
```powershell
cd c:\Users\gledston.carneiro\TRAE\auto-touch-droid
python backend\utils\ciclo_completo_todas_contas.py
```

## ⚙️ Configurações

### Device ID
O script usa o device ID configurado no arquivo `.env`:
```env
DEFAULT_DEVICE_ID=RXCTB03EXVK
```

Se o arquivo `.env` não existir, usa `RXCTB03EXVK` como padrão.

### Delays Configuráveis
Você pode ajustar os delays editando o arquivo:

```python
# Delays entre ações (em segundos)
DELAY_APOS_LOGIN = 3        # Aguarda após login bem-sucedido
DELAY_ENTRE_ACOES = 2       # Aguarda entre pegar baú e recursos
DELAY_APOS_LOGOUT = 5       # Aguarda após logout antes da próxima conta
DELAY_APOS_FALHA = 5        # Aguarda após falha antes de continuar
```

## 📊 Saída Esperada

### Durante a Execução
```
============================================================
  🚀 CICLO COMPLETO - TODAS AS CONTAS
============================================================
📱 Device ID: RXCTB03EXVK
👥 Total de contas: 10
⏰ Início da execução: 2025-11-24 15:45:00

📂 Carregando sequências de ações...
✅ Sequência de login carregada (11 passos)
✅ Sequência de logout carregada (X passos)
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

[... repete para cada conta ...]

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

## ⚠️ Tratamento de Erros

### Se uma conta falhar no login:
- O script **pula** as ações (baú e recursos)
- **Não tenta** fazer logout
- **Continua** para a próxima conta
- Registra a falha no resumo final

### Se uma ação falhar (baú ou recursos):
- O script **continua** com as próximas ações
- Tenta fazer **logout normalmente**
- **Não interrompe** o ciclo

### Se houver erro crítico:
- O script mostra o erro
- Aguarda alguns segundos
- **Continua** para a próxima conta

## 🛑 Interromper Execução

Para parar o script durante a execução:
- Pressione **Ctrl+C**
- O script mostrará quantas contas foram processadas
- Finalizará de forma controlada

## 📝 Logs

O script mostra informações detalhadas no console:
- ✅ Sucesso (verde)
- ⚠️ Avisos (amarelo)
- ❌ Erros (vermelho)
- 📊 Informações gerais
- ⏱️ Tempos de execução

## 🔧 Solução de Problemas

### Erro: "Nenhuma conta configurada"
**Solução:** Verifique se `backend/config/accounts_config.py` existe e tem contas definidas.

### Erro: "Não foi possível carregar sequência"
**Solução:** Verifique se os arquivos `sequence.json` existem em:
- `backend/actions/templates/fazer_login/sequence.json`
- `backend/actions/templates/fazer_logout/sequence.json`

### Erro: "device not found"
**Solução:** 
1. Verifique se o celular está conectado: `adb devices`
2. Reinicie o servidor ADB: `adb kill-server && adb start-server`
3. Verifique o device ID no `.env`

### Ações não encontradas
**Solução:** Verifique se as pastas existem:
- `backend/actions/templates/pegar_bau/`
- `backend/actions/templates/pegar_recursos/`

## 💡 Dicas

1. **Mantenha o celular desbloqueado** durante toda a execução
2. **Não use o celular** enquanto o script está rodando
3. **Bateria acima de 20%** recomendado
4. **Conexão USB estável** é essencial
5. **Primeira execução:** Teste com 1-2 contas primeiro

## 🧪 Teste Rápido

Para testar com apenas algumas contas, edite temporariamente `accounts_config.py`:

```python
# Teste com apenas 2 contas
accounts = [
    {"name": "login_gled"},
    {"name": "login_inf"},
]
```

Depois de testar, restaure todas as 10 contas.

## 📊 Tempo Estimado

- **Por conta:** ~30-60 segundos
- **10 contas:** ~5-10 minutos
- **Varia** conforme:
  - Velocidade do celular
  - Velocidade da conexão
  - Quantidade de baús/recursos
  - Delays configurados

## 🔄 Executar Periodicamente

Para executar automaticamente a cada X horas, você pode:

### Windows (Agendador de Tarefas)
1. Abra "Agendador de Tarefas"
2. Criar Tarefa Básica
3. Ação: Iniciar programa
4. Programa: `python`
5. Argumentos: `backend\utils\ciclo_completo_todas_contas.py`
6. Iniciar em: `c:\Users\gledston.carneiro\TRAE\auto-touch-droid`

### Script Batch (Windows)
Crie um arquivo `executar_ciclo.bat`:
```batch
@echo off
cd c:\Users\gledston.carneiro\TRAE\auto-touch-droid
python backend\utils\ciclo_completo_todas_contas.py
pause
```

## 📞 Suporte

Se tiver problemas:
1. Verifique os logs no console
2. Teste cada ação individualmente primeiro
3. Verifique a conexão ADB
4. Consulte `CONFIGURACAO_CELULAR.md` para problemas de conexão

---

**Boa sorte com a automação! 🚀**
