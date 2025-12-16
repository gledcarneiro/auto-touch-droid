# Walkthrough: Nova Estratégia de Login Implementada

**Data:** 2025-12-16  
**Versão:** 1.0  
**Autor:** Antigravity + Gled Carneiro

---

## Resumo das Mudanças

Implementamos com sucesso uma nova estratégia de login em `ciclo_rally_intercalado.py` que espelha a abordagem comprovada das filas de rally. A nova implementação usa:

1. **Template fixo único** (`prepara_tela_login.png`) em vez de templates individuais por conta
2. **Offsets de clique fixos** para contas 1-3 (visíveis sem scroll)
3. **Scroll cego parametrizado** para contas 4+ (configurável via JSON)
4. **Imagens de debug** para facilitar calibração dos offsets

---

## Arquivos Criados

### [login_scroll_config.json](file:///c:/Users/gledston.carneiro/TRAE/auto-touch-droid/backend/utils/login_scroll_config.json)

Novo arquivo de configuração com parâmetros de scroll para todas as 10 contas:

- **Contas 1-3**: `num_scrolls: 0` (sem scroll, apenas offsets fixos)
- **Contas 4-10**: Configuração completa de scroll cego com parâmetros ajustáveis:
  - `num_scrolls`: Quantidade de scrolls
  - `row_height`: Distância do scroll em pixels
  - `scroll_duration`: Duração do scroll em ms
  - `start_y` / `center_x`: Coordenadas do scroll
  - `offset_y`: Offset de clique após detecção do template

---

## Arquivos Modificados

### [ciclo_rally_intercalado.py](file:///c:/Users/gledston.carneiro/TRAE/auto-touch-droid/backend/utils/ciclo_rally_intercalado.py)

#### 1. Novas Constantes (linhas 81-87)

```python
TEMPLATE_PREPARA_TELA_LOGIN = os.path.join(backend_dir, "actions", "templates", "_global", "prepara_tela_login.png")
LOGIN_OFFSETS_FIXOS = {
    1: 140,
    2: 360,
    3: 590
}
LOGIN_OFFSET_CLICK_APOS_SCROLL = 650
```

#### 2. Nova Função `load_login_scroll_config()` (linhas 156-168)

Carrega configurações de scroll do arquivo JSON, similar à função existente para filas de rally.

#### 3. Nova Função `execute_login_with_fixed_template()` (linhas 171-288)

Função principal de login com a nova estratégia:

**Fluxo de execução:**
1. Clica no ícone do Google (passo 0 da sequência)
2. Aguarda tela de login carregar (2s)
3. **Se conta >= 4**: Executa scroll cego usando configuração do JSON
4. Captura tela e detecta template fixo `prepara_tela_login.png`
5. Calcula posição de clique: `centro_template_y + offset_y`
6. **Gera imagem de debug** mostrando:
   - Retângulo verde ao redor do template detectado
   - Círculo vermelho no ponto de clique
   - Linha azul mostrando o offset aplicado
   - Texto com número da conta e offset
7. Clica na posição calculada
8. Aguarda login completar (2s)

#### 4. Atualização `processar_fila_para_conta()` (linhas 414-448)

- Substituída chamada para `execute_login_for_account` por `execute_login_with_fixed_template`
- Adicionada lógica para encontrar índice da conta
- Passado parâmetro `login_scroll_config`

#### 5. Atualização `main()` (linhas 514-520, 559-563)

- Carrega `login_scroll_config` na inicialização
- Passa configuração para `processar_fila_para_conta`
- Exibe mensagem de confirmação do carregamento

---

## Geração de Imagens de Debug

### Localização

As imagens de debug são salvas em:
```
temp_screenshots/debug_login_conta_1.png
temp_screenshots/debug_login_conta_2.png
temp_screenshots/debug_login_conta_3.png
...
```

### Elementos Visuais

Cada imagem de debug contém:

| Elemento | Cor | Descrição |
|----------|-----|-----------|
| **Retângulo** | Verde | Área do template `prepara_tela_login.png` detectado |
| **Círculo** | Vermelho | Ponto exato onde o clique será executado |
| **Linha** | Azul | Mostra o offset aplicado do centro do template até o ponto de clique |
| **Texto** | Vermelho | Informações: "Conta X (+offset)" |

### Como Usar para Calibração

1. **Execute o script** para gerar as imagens de debug
2. **Abra as imagens** em `temp_screenshots/debug_login_conta_*.png`
3. **Verifique visualmente** se o círculo vermelho está posicionado corretamente sobre a conta desejada
4. **Se necessário ajustar**:
   - Abra `login_scroll_config.json`
   - Modifique o valor `offset_y` da conta correspondente
   - Para contas 4+, ajuste também `row_height` se o scroll não estiver correto
5. **Execute novamente** e verifique as novas imagens de debug

---

## Comparação: Antes vs Depois

### ❌ Abordagem Anterior

- Detectava templates individuais para cada conta (`02_login_gled.png`, `03_login_inf.png`, etc.)
- Usava `action_before_find` com scroll no JSON da sequência
- Difícil de calibrar (precisava ajustar múltiplos templates)
- Código complexo em `execute_login_for_account`

### ✅ Nova Abordagem

- Detecta **um único template fixo** (`prepara_tela_login.png`)
- Usa **scroll cego parametrizado** (igual às filas de rally)
- Fácil de calibrar com **imagens de debug visuais**
- Código mais simples e manutenível
- Configuração centralizada em **JSON externo**

---

## Próximos Passos

### Testes Recomendados

1. **Teste com Conta 1** (sem scroll):
   ```powershell
   python backend\utils\ciclo_rally_intercalado.py
   ```
   - Verificar se detecta template fixo
   - Verificar se clica na posição correta
   - Revisar `debug_login_conta_1.png`

2. **Teste com Conta 4** (com scroll):
   - Modificar temporariamente `CONTAS_ATIVAS = [3]` no código
   - Verificar se scroll cego executa corretamente
   - Revisar `debug_login_conta_4.png`

3. **Calibração de Offsets**:
   - Usar imagens de debug para ajustar `offset_y` no JSON
   - Testar iterativamente até obter precisão perfeita

4. **Teste Completo**:
   - Executar ciclo completo com todas as 3 contas ativas
   - Verificar taxa de sucesso de login
   - Comparar performance com abordagem anterior

### Ajustes Futuros (se necessário)

- **Offsets**: Ajustar valores em `login_scroll_config.json` baseado nas imagens de debug
- **Timing**: Ajustar delays (`time.sleep`) se necessário para estabilidade
- **Scroll**: Calibrar `row_height` para contas 4+ se scroll não estiver preciso

---

## Conclusão

✅ **Implementação concluída com sucesso!**

A nova estratégia de login está totalmente integrada e pronta para testes. As imagens de debug fornecerão feedback visual imediato para calibração precisa dos offsets, tornando o processo de ajuste muito mais fácil e intuitivo.

**Benefícios principais:**
- 🎯 Mais confiável (template fixo único)
- 🔧 Mais fácil de calibrar (debug visual)
- 📝 Mais fácil de manter (código mais limpo)
- ⚙️ Mais flexível (configuração JSON externa)

---

## Referências

- **Arquivo modificado:** [ciclo_rally_intercalado.py](file:///c:/Users/gledston.carneiro/TRAE/auto-touch-droid/backend/utils/ciclo_rally_intercalado.py)
- **Configuração:** [login_scroll_config.json](file:///c:/Users/gledston.carneiro/TRAE/auto-touch-droid/backend/utils/login_scroll_config.json)
- **Estratégia base:** [entrar_todos_rallys.py](file:///c:/Users/gledston.carneiro/TRAE/auto-touch-droid/backend/utils/entrar_todos_rallys.py) (scroll cego de filas)
