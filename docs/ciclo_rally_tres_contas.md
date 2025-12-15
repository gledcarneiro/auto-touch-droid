# Walkthrough: Script de Ciclo de Rally para 3 Contas

## 📋 Resumo

Foi criado o script **`ciclo_rally_tres_contas.py`** que automatiza a interação com três contas do jogo em um ciclo contínuo infinito.

## 🎯 Funcionalidades Implementadas

### 1. **Estrutura Base**
- Utiliza como referência o arquivo `ciclo_completo_todas_contas.py`
- Implementado para processar apenas as 3 primeiras contas (conta1, conta2, conta3)
- Mantém a mesma estrutura de imports e configurações do projeto

### 2. **Fluxo de Execução por Conta**

Cada conta passa pelo seguinte ciclo:

#### a) **Login**
- Implementa o mesmo mecanismo de autenticação do arquivo de exemplo
- Utiliza `execute_login_for_account()` com a sequência de login carregada
- Tratamento de erros com fallback para próxima conta em caso de falha

#### b) **Loop de Ações (9 Iterações)**
- Executa 9 iterações da ação `entrar_rallys`
- Implementa a lógica de **scroll cego progressivo** de `entrar_todos_rallys.py`:
  - Filas 1-3: Cliques em offsets fixos (140, 360, 590)
  - Filas 4-9: Scroll progressivo baseado em `scroll_config.json`
  - Detecção de template `03_fila.png` para localização
  - Sequência completa: Navegar → Scroll → Clicar Fila → Juntar → Tropas → Marchar
- Mantém os mesmos intervalos de tempo e verificações de segurança
- Sistema de status para controle de fluxo:
  - `MARCHED`: Rally concluído com sucesso
  - `NO_RALLY`: Fila vazia (fim da lista)
  - `NEXT`: Rally já participado
  - `REFRESH`: Template não encontrado
  - `ERROR`: Erro durante processamento

#### c) **Logout**
- Reset para tela principal (5x BACK) antes do logout
- Implementa o procedimento de logout seguro conforme exemplo
- Utiliza `execultar_acoes()` com a sequência de logout

#### d) **Repetição para Contas Subsequentes**
- Repete o mesmo processo (login → 9x rallys → logout) para conta2
- Repete o mesmo processo para conta3
- Delay configurável entre contas (padrão: 3s)

### 3. **Ciclo Contínuo**
- Após completar a conta3, retorna automaticamente para conta1
- Reinicia o ciclo indefinidamente
- Contador de ciclos para tracking
- Implementa verificações de erro a cada transição entre contas

### 4. **Requisitos Técnicos Atendidos**

#### ✅ **Logging Estruturado**
- Cabeçalhos formatados para cada seção
- Indicadores visuais (emojis) para diferentes tipos de mensagens
- Timestamps para início e término de cada conta/ciclo
- Resumo detalhado ao final de cada ciclo

#### ✅ **Tratamento de Erros**
- Try-catch em todas as operações críticas
- Fallback para próxima conta em caso de falha
- Delays após falhas para estabilização
- Interrupção segura via Ctrl+C

#### ✅ **Configurações**
- Device ID carregado do `.env` ou usa padrão
- Configurações de scroll carregadas de `scroll_config.json`
- Delays configuráveis entre ações
- Contas ativas definidas por índices (0, 1, 2)

## 📂 Localização e Nome

**Arquivo criado:** [ciclo_rally_tres_contas.py](file:///c:/Users/Gled/TRAE/auto-touch-droid/backend/utils/ciclo_rally_tres_contas.py)

**Localização:** `backend\utils\`

**Nome escolhido:** `ciclo_rally_tres_contas.py`
- Descritivo e auto-explicativo
- Indica claramente: ciclo + rally + três contas
- Segue o padrão de nomenclatura do projeto

## 🔧 Principais Funções

### `execute_account_cycle()`
Gerencia o ciclo completo de uma conta (Login → Rallys → Logout)

### `executar_rally_completo()`
Executa as 9 iterações de rally com scroll cego progressivo

### `processar_fila()`
Processa uma única fila com toda a lógica de scroll e cliques

### `navegar_para_lista_rallys()`
Garante navegação correta para a lista de rallys (Aliança → Batalha)

### `load_scroll_config()`
Carrega configurações de scroll do JSON

## 📊 Exemplo de Saída

```
================================================================================
  🚀 CICLO DE RALLY - 3 CONTAS (LOOP INFINITO)
================================================================================
📱 Device ID: RXCTB03EXVK
👥 Contas ativas: 3
🔄 Iterações de rally por conta: 9
⏰ Início da execução: 2025-12-14 08:30:37

📂 Carregando sequências de ações...
✅ Sequência de login carregada (X passos)
✅ Sequência de logout carregada (X passos)
✅ Sequência de rally carregada (X passos)
✅ Configurações de scroll carregadas do scroll_config.json

================================================================================
  🔁 CICLO #1
================================================================================

================================================================================
  CONTA 1/3: conta1
================================================================================
⏰ Início: 08:30:45

[1/3] LOGIN - conta1
✅ Login bem-sucedido: conta1

[2/3] EXECUTAR RALLYS - conta1
🎯 EXECUTANDO RALLYS - conta1
...
📊 Total de rallies participados: 5

[3/3] LOGOUT - conta1
✅ Logout bem-sucedido: conta1

⏱️ Tempo total para conta1: 120.5s
⏰ Término: 08:32:45

[Repete para conta2 e conta3...]

================================================================================
  📊 RESUMO DO CICLO #1
================================================================================
✅ Contas processadas com sucesso: 3
❌ Contas com falha: 0
⏱️ Tempo do ciclo: 360.2s (6.0 min)
⏰ Término do ciclo: 08:36:45

🎉 CICLO #1 COMPLETO! Reiniciando para conta1...
```

## ✨ Diferenciais

1. **Scroll Cego Progressivo**: Implementação fiel da lógica de `entrar_todos_rallys.py`
2. **Otimização de Navegação**: Flag `jah_na_lista` evita navegação redundante
3. **Ciclo Infinito Robusto**: Reinicia automaticamente após completar as 3 contas
4. **Logging Detalhado**: Facilita debugging e monitoramento
5. **Tratamento de Erros Completo**: Continua operação mesmo com falhas pontuais

## 🚀 Como Usar

```bash
cd c:\Users\Gled\TRAE\auto-touch-droid\backend\utils
python ciclo_rally_tres_contas.py
```

**Interromper:** Pressione `Ctrl+C` para parar o ciclo de forma segura.
