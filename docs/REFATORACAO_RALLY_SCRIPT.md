# 🔧 REFATORAÇÃO COMPLETA - entrar_todos_rallys.py

## 📋 **MUDANÇAS IMPLEMENTADAS**

### ✅ **1. NAVEGAÇÃO INICIAL (PARTE 1 e 2) - EXECUTADA 1x POR CICLO**

**Antes:** ❌ Executava Aliança→Batalha **a cada fila** (9x por ciclo!)

**Depois:** ✅ Executa Aliança→Batalha **1x por ciclo** no início

```python
# PARTE 1 e 2: NAVEGAÇÃO INICIAL (executar apenas 1x por ciclo)
# Tela0 → Tela1 (Aliança → Batalha)
sequence_inicial = rally_sequence[0:2]  # passos 1-2
success_inicial = execultar_acoes(...)

if not success_inicial:
    print("❌ Falha na navegação inicial")
    continue  # Reinicia o ciclo (já está na Tela0)

# Agora está na Tela1 (Aba das Filas)
# Loop de filas começa aqui...
```

---

### ✅ **2. SCROLL INCREMENTAL CORRIGIDO**

**Duração base aumentada:** 150ms → **200ms** (mais força)

**Lógica:**
```python
Fila 4: 200ms (1x base) - scroll leve
Fila 5: 400ms (2x base) - scroll médio
Fila 6: 600ms (3x base) - scroll forte
Fila 7: 800ms (4x base)
Fila 8: 1000ms (5x base)
Fila 9: 1200ms (6x base)
```

**Maior duração = Scroll mais lento = Mais força = Move mais filas**

---

### ✅ **3. FLUXO SEPARADO EM 6 PARTES (Conforme solicitado)**

```
PARTE 1: Tela0 - Clicar em Aliança (01_alianca.png)
PARTE 2: Tela1 - Clicar em Batalha (02_batalha.png)
PARTE 3: Tela1 - Scroll + Clicar na Fila (03_fila.png)
PARTE 4: Tela2 - Clicar em Juntar (04_juntar.png)
PARTE 5: Tela3 - Clicar em Tropas (05_tropas.png) ⚠️ FALHA ESPERADA
PARTE 6: Tela3 - Clicar em Marchar (06_marchar.png)
```

---

### ✅ **4. TRATAMENTO DE FALHAS CORRETO**

#### **PARTE 4 - Falha em "Juntar":**
```python
if not success_juntar:
    print("⚠️ Botão 'Juntar' não encontrado ou desabilitado")
    print("🔙 Voltando para Tela1 (1x BACK)")
    subprocess.run(["adb", "-s", DEVICE_ID, "shell", "input", "keyevent", "4"])
    continue  # Pula para próxima fila
```

#### **PARTE 5 - Falha em "Tropas" (FALHA ESPERADA):**
```python
if not success_tropas:
    # Tela3 não abriu = Já estamos nesta fila
    print("⚠️ [FALHA ESPERADA] 05_tropas não encontrado - Já estamos nesta fila!")
    print("🔙 Voltando para Tela1 (1x BACK)")
    subprocess.run(["adb", "-s", DEVICE_ID, "shell", "input", "keyevent", "4"])
    
    # Fazer scroll adicional se fila >= 3
    if fila_num >= 3:
        simulate_scroll(device_id=DEVICE_ID, direction="up", duration_ms=200)
    
    continue  # Próxima fila
```

#### **PARTE 6 - Sucesso em "Marchar":**
```python
if success_marchar:
    print("✅ Fila processada com SUCESSO!")
    # Garantir que voltou à Tela1 (5x BACK por segurança)
    for _ in range(5):
        subprocess.run(["adb", "-s", DEVICE_ID, "shell", "input", "keyevent", "4"])
```

---

### ✅ **5. LOGS MELHORADOS**

```
🏁 INICIANDO NAVEGAÇÃO: Aliança → Batalha
✅ Navegação OK - Tela1 (Aba das Filas) aberta

🎯 PROCESSANDO FILA 1/9
📍 Fila 1: Offset fixo de 140px
🔍 [PARTE 3] Detectando e clicando na fila 1
✅ Template encontrado em (x, y)
👆 Clicando com offset +140px → (x, y)
🔘 [PARTE 4] Clicando em 'Juntar' (04_juntar.png)
✅ 'Juntar' clicado - Tela3 deve abrir
👥 [PARTE 5] Clicando em 'Tropas' (05_tropas.png)
✅ 'Tropas' clicado
⚔️ [PARTE 6] Clicando em 'Marchar' (06_marchar.png)
✅ Fila 1 processada com SUCESSO!
🔙 Voltando para Tela1 (5x BACK por segurança)
```

---

## 📊 **FLUXO COMPLETO**

```
┌─────────────────────────────────────────────────────────┐
│  CICLO INFINITO 24/7                                    │
└─────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│  PARTE 1 e 2: Navegação Inicial (1x por ciclo)         │
│  ├─ Tela0 → Clicar Aliança                             │
│  └─ Tela1 → Clicar Batalha                             │
└─────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────┐
│  LOOP DE FILAS (1 a 9)                                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  PARTE 3: Scroll (se fila >= 4) + Clicar Fila          │
│  ├─ Fila 1-3: Offset fixo (140/360/590)                │
│  └─ Fila 4+: Scroll incremental + Offset 590px         │
│                                                          │
│  PARTE 4: Clicar "Juntar" (Tela1 → Tela2)              │
│  └─ Se falhar → BACK → Próxima fila                    │
│                                                          │
│  PARTE 5: Clicar "Tropas" (Tela2 → Tela3)              │
│  └─ Se falhar (ESPERADO) → BACK → Scroll → Próxima     │
│                                                          │
│  PARTE 6: Clicar "Marchar" (Tela3 → Tela0)             │
│  └─ 5x BACK para garantir volta à Tela1                │
│                                                          │
└─────────────────────────────────────────────────────────┘
           │
           ▼
    Aguardar 3s e reiniciar ciclo
```

---

## 🎯 **PARÂMETROS AJUSTÁVEIS**

```python
# Linha ~116
SCROLL_BASE_DURATION = 200  # Aumentar se scroll fraco
                            # Diminuir se scroll muito forte

# Linhas ~109-113
OFFSETS_FIXOS = {
    1: 140,   # Ajustar se clicar errado na fila 1
    2: 360,   # Ajustar se clicar errado na fila 2
    3: 590,   # Ajustar se clicar errado na fila 3
}
```

---

## 🧪 **COMO TESTAR**

1. **Parar o script atual:** Ctrl+C
2. **Reiniciar:**
   ```bash
   python .\backend\utils\entrar_todos_rallys.py
   ```
3. **Observar:**
   - Aliança→Batalha executado **1x no início**
   - Scroll incremental para filas 4+ (200ms, 400ms, 600ms...)
   - Tratamento correto de falhas (1x BACK, não 5x)
   - Screenshots de debug salvos

---

## ⚠️ **PONTOS DE ATENÇÃO**

1. **Scroll Base Duration (200ms):**
   - Se filas 4+ não estiverem na posição correta → **Aumentar**
   - Se scroll muito forte → **Diminuir**

2. **Falha em "Tropas":**
   - É **ESPERADA** quando já está na fila
   - Script faz 1x BACK e continua para próxima
   - Se fila >= 3, faz scroll adicional de 200ms

3. **Volta à Tela1:**
   - Após sucesso: 5x BACK (garantir volta)
   - Após falha: 1x BACK (já está perto)

---

## 📈 **MELHORIAS IMPLEMENTADAS**

✅ Navegação inicial 1x por ciclo (não 9x)  
✅ Scroll incremental correto (200ms base)  
✅ Fluxo separado em 6 partes claras  
✅ Tratamento de falhas específico por parte  
✅ Logs detalhados com identificação de parte  
✅ 1x BACK para falhas, 5x BACK para sucessos  
✅ Continue em vez de break para pular filas  

---

**Desenvolvido com ❤️ pela Claude-Gled Partnership** ✨
