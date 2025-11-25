# 🔧 AJUSTE DE SCROLLS - Sequence.json do Login

## 📋 Problema Identificado

A partir da **conta 4 (login_c52)**, os templates não apareciam na tela porque apenas **3 contas ficam visíveis** por vez na lista de contas do Google.

### Comportamento Observado:
- **Contas 1-3** (gled, inf, cav): ✅ Visíveis sem scroll
- **Contas 4-10** (c52 até c58): ❌ Precisam de scroll para aparecer

---

## ✅ Solução Implementada

Ajustei o arquivo `backend/actions/templates/fazer_login/sequence.json` com **scrolls incrementais** para cada conta a partir da 4ª.

### Scrolls Configurados:

| Conta | Template | Scroll (ms) | Motivo |
|-------|----------|-------------|--------|
| 1 - login_gled | 02_login_gled.png | **0** | Visível sem scroll |
| 2 - login_inf | 03_login_inf.png | **0** | Visível sem scroll |
| 3 - login_cav | 04_login_cav.png | **0** | Visível sem scroll |
| 4 - login_c52 | 05_login_c52.png | **300ms** | 1º scroll (pequeno) |
| 5 - login_c53 | 06_login_c53.png | **600ms** | 2º scroll (médio) |
| 6 - login_c54 | 07_login_c54.png | **900ms** | 3º scroll |
| 7 - login_c55 | 08_login_c55.png | **1200ms** | 4º scroll |
| 8 - login_c56 | 09_login_c56.png | **1500ms** | 5º scroll |
| 9 - login_c57 | 10_login_c57.png | **1800ms** | 6º scroll |
| 10 - login_c58 | 11_login_c58.png | **2100ms** | 7º scroll (maior) |

---

## 🔍 Como Funciona

### Estrutura do JSON (Exemplo - Conta 5):

```json
{
    "name": "Passo 6: Template 06_login_c53.png",
    "type": "template",
    "template_file": "06_login_c53.png",
    "action_on_found": "click",
    "action_before_find": { 
        "type": "scroll",
        "direction": "up",
        "duration_ms": 600,
        "delay_after_scroll": 1.5
    },
    "click_delay": 0.5,
    "click_offset": [0, 0],
    "max_attempts": 5,
    "attempt_delay": 1.0,
    "initial_delay": 2.0
}
```

### Fluxo de Execução:

1. **action_before_find** - Executa ANTES de buscar o template
2. **Scroll UP** - Sobe a lista de contas
3. **duration_ms** - Duração do scroll (quanto maior, mais sobe)
4. **delay_after_scroll** - Aguarda 1.5s para a tela estabilizar
5. **Busca o template** - Agora o template está visível
6. **Clica** - Se encontrar o template

---

## 📊 Progressão dos Scrolls

Os scrolls aumentam **300ms a cada conta**:

```
Conta 4: 300ms   (1 unidade de scroll)
Conta 5: 600ms   (2 unidades de scroll)
Conta 6: 900ms   (3 unidades de scroll)
Conta 7: 1200ms  (4 unidades de scroll)
Conta 8: 1500ms  (5 unidades de scroll)
Conta 9: 1800ms  (6 unidades de scroll)
Conta 10: 2100ms (7 unidades de scroll)
```

Esta progressão garante que:
- Cada conta subsequente fica visível após o scroll
- O template pode ser detectado corretamente
- O clique acontece no lugar certo

---

## 🧪 Testando os Ajustes

### Teste Individual (Uma Conta):

```bash
# Teste a conta 4 (primeira que precisa de scroll)
python backend/utils/teste_ciclo_uma_conta.py
# Edite CONTA_TESTE_INDEX = 3  # (índice 3 = conta 4 = login_c52)
```

### Teste Completo (Todas as Contas):

```bash
python backend/utils/ciclo_completo_todas_contas.py
```

---

## 🔧 Ajustes Finos (Se Necessário)

### Se o scroll for muito pouco:
Aumente os valores de `duration_ms`:

```json
"duration_ms": 400,  // Era 300
"duration_ms": 800,  // Era 600
// etc.
```

### Se o scroll for muito:
Diminua os valores de `duration_ms`:

```json
"duration_ms": 200,  // Era 300
"duration_ms": 400,  // Era 600
// etc.
```

### Se precisar de mais tempo para estabilizar:
Aumente `delay_after_scroll`:

```json
"delay_after_scroll": 2.0  // Era 1.5
```

---

## 💡 Dicas

1. **Primeira execução:** Observe se os templates estão sendo encontrados
2. **Se falhar:** Aumente os valores de scroll gradualmente
3. **Logs:** Verifique os logs para ver se o template foi encontrado
4. **Tela do celular:** Observe se a conta fica visível após o scroll

---

## 📝 Exemplo de Log Esperado (Conta 4):

```
[1/4] LOGIN - login_c52

Executando ação antes de encontrar template: Scroll.
Simulando scroll genérico OTIMIZADO na direção 'up'.
DEBUG simulate_scroll command: adb -s RXCTB03EXVK shell input swipe 1200 810 1200 270 300
Scroll simulado com sucesso.

🔍 PROCURANDO TEMPLATE: 05_login_c52.png
Tentativa 1/5 para encontrar o template '05_login_c52.png'.
Template '05_login_c52.png' encontrado na tentativa 1 em (X, Y).
✅ TEMPLATE ENCONTRADO!
👆 CLICANDO EM: (X, Y)
```

---

## ✅ Resultado Esperado

Agora **todas as 10 contas** devem funcionar corretamente:

- ✅ Contas 1-3: Sem scroll (como antes)
- ✅ Contas 4-10: Com scroll incremental (NOVO)
- ✅ Templates detectados corretamente
- ✅ Cliques no lugar certo
- ✅ Ciclo completo funcional

---

## 🔄 Se Ainda Houver Problemas

### Problema: Template não encontrado mesmo com scroll

**Possíveis causas:**
1. Scroll insuficiente → Aumente `duration_ms`
2. Tela não estabilizou → Aumente `delay_after_scroll`
3. Template diferente → Recrie o template
4. Resolução diferente → Verifique resolução do celular

### Problema: Scroll demais (passou da conta)

**Solução:**
- Diminua `duration_ms` gradualmente
- Teste com valores menores (200ms, 400ms, etc.)

---

**Ajustes concluídos! Teste agora o ciclo completo! 🚀**

*Atualizado em: 24/11/2025 16:40*
