# 📜 Sistema de Scroll Configurável - Rally Bot

## 📋 Visão Geral

Sistema de calibração manual de scroll para o Rally Bot, permitindo ajuste fino individual para cada fila (4-9) sem modificar o código principal.

## 🗂️ Arquivos do Sistema

### 1. `scroll_config.json`
Arquivo de configuração com parâmetros individuais de scroll para cada fila.

**Parâmetros por fila:**
- `num_scrolls`: Quantidade de scrolls a executar
- `row_height`: Distância em pixels (quanto maior, mais sobe a lista)
- `scroll_duration`: Duração em milissegundos (1000 = 1 segundo)
- `start_y`: Coordenada Y inicial do scroll
- `center_x`: Coordenada X do scroll (centro da lista)

### 2. `teste_scroll.py`
Script interativo para calibração manual de scroll.

### 3. `entrar_todos_rallys.py` (v4.2)
Bot principal atualizado para usar configurações do JSON.

---

## 🚀 Como Usar

### Passo 1: Executar o Script de Teste

```bash
python backend\utils\teste_scroll.py
```

### Passo 2: Menu Interativo

O script oferece as seguintes opções:

- **[1-9]** - Testar scroll para fila específica
- **[A]** - Testar todas as filas (4-9) em sequência
- **[E]** - Editar configuração de uma fila
- **[V]** - Visualizar configurações atuais
- **[R]** - Reset (voltar para tela inicial)
- **[S]** - Sair

### Passo 3: Calibração

1. **Escolha uma fila para testar** (ex: digite `5` para Fila 5)
2. O script irá:
   - Navegar para a lista de rallys
   - Executar o scroll configurado
   - Capturar screenshot com marcações visuais
   - Salvar em `temp_screenshots/calibracao_fila_X.png`

3. **Analise o screenshot:**
   - **Linha amarela horizontal** = Posição ideal (offset)
   - **Círculo vermelho** = Onde o bot vai clicar
   - **Retângulo verde** = Template detectado

4. **Ajuste conforme necessário:**
   - Se a fila estiver **ACIMA** da linha amarela → **DIMINUA** `row_height`
   - Se a fila estiver **ABAIXO** da linha amarela → **AUMENTE** `row_height`

### Passo 4: Editar Configuração

1. No menu, digite **E**
2. Escolha a fila (4-9)
3. Escolha o parâmetro a editar
4. Digite o novo valor
5. A configuração é salva automaticamente no JSON

### Passo 5: Validar

Teste novamente a fila para confirmar que o ajuste funcionou.

---

## 🎯 Guia de Calibração Rápida

### Problema: Fila aparece muito acima do ponto de clique

**Solução:** Diminuir `row_height`

```json
"5": {
  "num_scrolls": 2,
  "row_height": 220,  // Era 230, diminuiu 10px
  "scroll_duration": 1000,
  "start_y": 800,
  "center_x": 1200
}
```

### Problema: Fila aparece muito abaixo do ponto de clique

**Solução:** Aumentar `row_height`

```json
"8": {
  "num_scrolls": 5,
  "row_height": 240,  // Era 230, aumentou 10px
  "scroll_duration": 1000,
  "start_y": 800,
  "center_x": 1200
}
```

### Problema: Scroll muito rápido/brusco

**Solução:** Aumentar `scroll_duration`

```json
"6": {
  "num_scrolls": 3,
  "row_height": 230,
  "scroll_duration": 1200,  // Era 1000, mais lento
  "start_y": 800,
  "center_x": 1200
}
```

### Problema: Scroll muito lento

**Solução:** Diminuir `scroll_duration`

```json
"7": {
  "num_scrolls": 4,
  "row_height": 230,
  "scroll_duration": 800,  // Era 1000, mais rápido
  "start_y": 800,
  "center_x": 1200
}
```

---

## 📊 Valores Padrão Iniciais

Todas as filas 4-9 começam com:
- `row_height`: 230px
- `scroll_duration`: 1000ms
- `start_y`: 800
- `center_x`: 1200
- `num_scrolls`: (fila - 3)

---

## 🔍 Interpretando os Screenshots

### Elementos Visuais:

1. **Retângulo Verde** 🟢
   - Template `03_fila.png` detectado
   - Mostra onde o bot encontrou a referência

2. **Círculo Vermelho** 🔴
   - Ponto exato onde o bot vai clicar
   - Calculado como: Centro do template + Offset

3. **Linha Azul** 🔵
   - Mostra o offset aplicado
   - Conecta o centro do template ao ponto de clique

4. **Linha Amarela Horizontal** 🟡
   - Posição ideal (target)
   - A fila deve estar alinhada com esta linha

5. **Textos Informativos**
   - Número da fila
   - Valor do offset
   - Coordenada Y do clique

---

## ⚙️ Configuração Avançada

### Ajuste de Posição Horizontal

Se precisar ajustar a posição X do scroll:

```json
"9": {
  "num_scrolls": 6,
  "row_height": 230,
  "scroll_duration": 1000,
  "start_y": 800,
  "center_x": 1150  // Moveu 50px para esquerda
}
```

### Ajuste de Ponto Inicial

Se precisar começar o scroll de outra posição:

```json
"4": {
  "num_scrolls": 1,
  "row_height": 230,
  "scroll_duration": 1000,
  "start_y": 850,  // Começou 50px mais abaixo
  "center_x": 1200
}
```

---

## 🐛 Troubleshooting

### Erro: "scroll_config.json não encontrado"
- Certifique-se de que o arquivo está em `backend/utils/scroll_config.json`
- O bot usará valores padrão se o arquivo não existir

### Erro: "Template 03_fila.png não encontrado"
- Verifique se está na tela de lista de rallys
- Use a opção [R] para resetar e tentar novamente

### Screenshot não é salvo
- Verifique se a pasta `temp_screenshots/` existe
- Certifique-se de que o OpenCV (cv2) está instalado

### Scroll não funciona como esperado
- Teste com incrementos pequenos (±5px por vez)
- Valide cada ajuste antes de testar a próxima fila
- Lembre-se: cada fila é independente!

---

## 📝 Workflow Recomendado

1. **Teste inicial:** Use opção [A] para testar todas as filas
2. **Identifique problemas:** Analise os screenshots salvos
3. **Ajuste fino:** Use opção [E] para editar filas problemáticas
4. **Valide:** Teste individualmente cada fila ajustada
5. **Repita:** Continue até todas as filas estarem calibradas
6. **Execute o bot:** Use `entrar_todos_rallys.py` normalmente

---

## 🎓 Dicas de Calibração

- **Comece com ajustes pequenos:** ±5-10px por vez
- **Teste uma fila por vez:** Não ajuste múltiplas filas simultaneamente
- **Documente seus ajustes:** Anote o que funcionou
- **Considere o contexto:** Filas mais distantes podem precisar de ajustes maiores
- **Seja paciente:** Calibração precisa leva tempo, mas vale a pena!

---

## 📌 Notas Importantes

- ⚠️ **Backup:** Faça backup do `scroll_config.json` antes de grandes mudanças
- 🔄 **Reload automático:** O bot carrega as configurações a cada execução
- 🎯 **Precisão:** Ajustes de 5-10px geralmente são suficientes
- 📸 **Screenshots:** São salvos com timestamp para histórico

---

## 🆘 Suporte

Se encontrar problemas:
1. Verifique os logs do `teste_scroll.py`
2. Analise os screenshots em `temp_screenshots/`
3. Revise as configurações no `scroll_config.json`
4. Teste com valores padrão primeiro

---

**Versão:** 1.0  
**Última Atualização:** 2025-12-05  
**Compatível com:** Rally Bot v4.2+
