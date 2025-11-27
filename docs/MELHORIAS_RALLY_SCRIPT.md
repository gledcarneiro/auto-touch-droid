# 🔧 MELHORIAS NO SCRIPT `entrar_todos_rallys.py`

## 📋 **RESUMO DAS ALTERAÇÕES**

Baseado na análise dos screenshots e comportamento do jogo, foram implementadas as seguintes melhorias:

---

## ✅ **1. CORREÇÃO DOS OFFSETS FIXOS**

### **Antes (INCORRETO):**
```python
if fila_num == 1:
    offset_y = 140
elif fila_num == 2:
    offset_y = 220  # ❌ ERRADO
else:
    offset_y = 310  # ❌ ERRADO
```

### **Depois (CORRETO):**
```python
OFFSETS_FIXOS = {
    1: 140,   # Fila 1 (primeira visível)
    2: 360,   # Fila 2 (segunda visível) ✅
    3: 590,   # Fila 3 (terceira visível) ✅
}
OFFSET_CLICK_APOS_SCROLL = 590  # Sempre clicar na posição da fila 3 após scroll
```

**Motivo:** Os screenshots mostraram que os offsets corretos são 140, 360 e 590 pixels.

---

## ✅ **2. SCROLL INCREMENTAL PARA FILAS 4+**

### **Nova Lógica:**
```python
if fila_num >= 4:
    num_scrolls = fila_num - 3
    scroll_duration = SCROLL_BASE_DURATION * num_scrolls
    
    # Fila 4: 150ms (1 scroll)
    # Fila 5: 300ms (2 scrolls)
    # Fila 6: 450ms (3 scrolls)
    # etc.
```

**Motivo:** Cada fila adicional precisa de mais scroll para trazer a fila para a posição da Fila 3 (590px).

---

## ✅ **3. SEMPRE CLICAR EM 590PX APÓS SCROLL**

### **Nova Lógica:**
```python
if fila_num in OFFSETS_FIXOS:
    offset_y = OFFSETS_FIXOS[fila_num]  # 140, 360 ou 590
else:
    offset_y = OFFSET_CLICK_APOS_SCROLL  # Sempre 590px para filas 4+
```

**Motivo:** O template `03_fila.png` está em posição fixa. Após o scroll, a próxima fila sempre aparece na posição da Fila 3.

---

## ✅ **4. MELHOR TRATAMENTO DE FALHA (Já está na fila)**

### **Antes:**
- Voltava (BACK)
- Calculava `next_offset_y = offset_y + 140` ❌
- Tentava clicar na "próxima fila" com offset errado

### **Depois:**
- Volta (BACK)
- Faz scroll adicional (se fila >= 3)
- **Deixa o loop continuar naturalmente** para a próxima iteração
- A próxima iteração vai processar a fila seguinte com offset correto

**Motivo:** A estratégia anterior de incrementar offset manualmente estava causando cliques em posições erradas.

---

## ✅ **5. FLUXO REORGANIZADO EM 5 PARTES**

```
PARTE 1: Navegação Inicial (Aliança → Batalha)
PARTE 2: Scroll (se fila >= 4)
PARTE 3: Detectar Template e Clicar na Fila
PARTE 4: Executar Sequência (Juntar → Tropas → Marchar)
PARTE 5: Tratamento de Falha (já está na fila)
```

**Motivo:** Código mais organizado e fácil de debugar.

---

## 📊 **COMPORTAMENTO ESPERADO**

### **Filas 1-3 (Visíveis sem scroll):**
```
Fila 1: Offset 140px  → Clicar → Executar sequência
Fila 2: Offset 360px  → Clicar → Executar sequência
Fila 3: Offset 590px  → Clicar → Executar sequência
```

### **Filas 4-9 (Requerem scroll):**
```
Fila 4: Scroll 150ms  → Offset 590px → Clicar → Executar sequência
Fila 5: Scroll 300ms  → Offset 590px → Clicar → Executar sequência
Fila 6: Scroll 450ms  → Offset 590px → Clicar → Executar sequência
Fila 7: Scroll 600ms  → Offset 590px → Clicar → Executar sequência
Fila 8: Scroll 750ms  → Offset 590px → Clicar → Executar sequência
Fila 9: Scroll 900ms  → Offset 590px → Clicar → Executar sequência
```

---

## 🐛 **TRATAMENTO DE FALHA (Já está na fila)**

### **Cenário:**
`05_tropas.png` não é encontrado (botão desabilitado)

### **Ação:**
1. ✅ Volta (BACK) para lista de filas
2. ✅ Se fila >= 3: Faz scroll adicional de 150ms
3. ✅ Continua para próxima iteração do loop
4. ✅ Próxima fila será processada com offset correto

**Exemplo:**
```
Fila 2: Falhou (já na fila)
  → BACK
  → Sem scroll adicional (fila < 3)
  → Próxima iteração: Fila 3 com offset 590px ✅

Fila 5: Falhou (já na fila)
  → BACK
  → Scroll adicional 150ms
  → Próxima iteração: Fila 6 com scroll 450ms + offset 590px ✅
```

---

## 🎯 **MELHORIAS ADICIONAIS**

1. **Tempos ajustados:**
   - Scroll: 150ms base (incremental)
   - Aguardar após scroll: 1.5s (estabilização)
   - Aguardar após clique: 1.0s

2. **Debug melhorado:**
   - Screenshots mostram número da fila no texto
   - Logs mais claros com separadores

3. **Recuperação de erros:**
   - Sempre volta à tela inicial em caso de erro
   - Aguarda 2s antes de reiniciar ciclo

---

## 🚀 **PRÓXIMOS PASSOS**

1. **Testar o script** com as novas mudanças
2. **Verificar screenshots de debug** para confirmar cliques corretos
3. **Ajustar `SCROLL_BASE_DURATION`** se necessário (atualmente 150ms)
4. **Reportar resultados** para ajustes finos

---

## ⚙️ **PARÂMETROS AJUSTÁVEIS**

Se precisar ajustar:

```python
# Linha ~116
SCROLL_BASE_DURATION = 150  # Aumentar se scroll muito rápido
                            # Diminuir se scroll muito lento

# Linha ~109-113
OFFSETS_FIXOS = {
    1: 140,   # Ajustar se clicar errado na fila 1
    2: 360,   # Ajustar se clicar errado na fila 2
    3: 590,   # Ajustar se clicar errado na fila 3
}
```

---

**Desenvolvido com ❤️ pela Claude-Gled Partnership** ✨
