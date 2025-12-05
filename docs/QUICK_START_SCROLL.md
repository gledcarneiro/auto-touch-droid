# 🎯 RESUMO - Sistema de Scroll Configurável

## ✅ Arquivos Criados

1. **scroll_config.json** - Configurações individuais por fila
2. **teste_scroll.py** - Script de calibração interativo
3. **README_SCROLL_CONFIG.md** - Documentação completa
4. **entrar_todos_rallys.py** - Atualizado para v4.2

---

## 🚀 Como Começar (Quick Start)

### 1️⃣ Execute o teste de scroll:
```bash
python backend\utils\teste_scroll.py
```

### 2️⃣ No menu, escolha uma opção:
- Digite `5` para testar a Fila 5
- Digite `A` para testar todas as filas
- Digite `E` para editar configurações

### 3️⃣ Analise o screenshot:
- Procure em: `temp_screenshots/calibracao_fila_X.png`
- **Linha amarela** = posição ideal
- **Círculo vermelho** = onde vai clicar

### 4️⃣ Ajuste se necessário:
- Fila **ACIMA** da linha → **DIMINUA** row_height
- Fila **ABAIXO** da linha → **AUMENTE** row_height

---

## 📊 Estrutura do scroll_config.json

```json
{
  "filas": {
    "4": {
      "num_scrolls": 1,      // Quantos scrolls
      "row_height": 230,     // Distância (px)
      "scroll_duration": 1000, // Velocidade (ms)
      "start_y": 800,        // Início Y
      "center_x": 1200       // Posição X
    },
    "5": { ... },
    "6": { ... },
    // ... até fila 9
  }
}
```

---

## 🎨 Interpretando Screenshots

```
┌─────────────────────────────────────┐
│                                     │
│  🟢 Retângulo Verde                 │
│  └─ Template detectado              │
│                                     │
│  🔵 Linha Azul                      │
│  └─ Offset aplicado                 │
│                                     │
│  🟡 Linha Amarela ═══════════════   │ ← Posição IDEAL
│  └─ Target (onde deve estar)       │
│                                     │
│  🔴 Círculo Vermelho                │
│  └─ Ponto de clique                 │
│                                     │
└─────────────────────────────────────┘
```

---

## 🔧 Ajustes Comuns

### Fila muito acima:
```json
"row_height": 220  // Era 230, diminuiu
```

### Fila muito abaixo:
```json
"row_height": 240  // Era 230, aumentou
```

### Scroll muito rápido:
```json
"scroll_duration": 1200  // Era 1000, mais lento
```

---

## 📝 Workflow de Calibração

```
1. Testar fila → 2. Ver screenshot → 3. Ajustar config → 4. Repetir
     ↑                                                        ↓
     └────────────────────────────────────────────────────────┘
```

---

## ⚡ Comandos Rápidos

| Comando | Ação |
|---------|------|
| `1-9` | Testar fila específica |
| `A` | Testar todas (4-9) |
| `E` | Editar configuração |
| `V` | Ver configs atuais |
| `R` | Reset (5x BACK) |
| `S` | Sair |

---

## 🎯 Valores Iniciais (Todas as Filas 4-9)

- `row_height`: **230px**
- `scroll_duration`: **1000ms**
- `start_y`: **800**
- `center_x`: **1200**
- `num_scrolls`: **(fila - 3)**

---

## 💡 Dicas

✅ Ajuste de **5-10px** por vez  
✅ Teste **uma fila** de cada vez  
✅ **Backup** do JSON antes de mudanças  
✅ Screenshots ficam em `temp_screenshots/`  

---

## 🐛 Problemas Comuns

**Q: JSON não encontrado?**  
A: Bot usa valores padrão automaticamente

**Q: Template não detectado?**  
A: Use [R] para resetar e voltar à tela inicial

**Q: Screenshot não salva?**  
A: Verifique se `temp_screenshots/` existe

---

## 📞 Próximos Passos

1. ✅ Execute `teste_scroll.py`
2. ✅ Calibre as filas problemáticas (5 e 8)
3. ✅ Valide com testes individuais
4. ✅ Execute o bot normalmente

**Boa calibração! 🎯**
