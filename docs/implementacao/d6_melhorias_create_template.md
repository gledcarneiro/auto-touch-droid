# 📝 MELHORIAS PARA create_action_template.py

## 🎯 Melhorias Propostas

### 1. **Adicionar Suporte a Scrolls Automáticos**
**Problema:** Atualmente não tem opção fácil para adicionar scrolls
**Solução:** Adicionar pergunta após criar template se precisa de scroll

```python
# Após criar template, perguntar:
needs_scroll = input("Este passo precisa de scroll antes de buscar? (s/n): ").lower()
if needs_scroll == 's':
    scroll_duration = input("Duração do scroll em ms (padrão 300): ")
    scroll_duration = int(scroll_duration) if scroll_duration else 300
    
    step_config["action_before_find"] = {
        "type": "scroll",
        "direction": "up",
        "duration_ms": scroll_duration,
        "delay_after_scroll": 1.5
    }
```

### 2. **Melhorar Visualização da Marcação**
**Problema:** Usuário não vê preview da área marcada
**Solução:** Mostrar preview antes de salvar

```python
# Após detectar marcação, mostrar preview
if mark_position:
    x, y, w, h = mark_position
    preview = original_for_crop.copy()
    cv2.rectangle(preview, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.imshow("Preview da Area Marcada", preview)
    cv2.waitKey(2000)  # Mostra por 2 segundos
    cv2.destroyAllWindows()
    
    confirm = input("Area correta? (s/n): ").lower()
    if confirm != 's':
        print("Marcação rejeitada. Tente novamente.")
        return None
```

### 3. **Adicionar Modo Batch para Múltiplos Templates**
**Problema:** Para rallys, precisa criar 11 templates similares
**Solução:** Modo batch que cria vários templates de uma vez

```python
def create_multiple_templates_batch(action_name, count, device_id=None):
    """
    Cria múltiplos templates de uma vez (útil para rallys)
    
    Args:
        action_name: Nome da ação
        count: Quantidade de templates a criar
        device_id: ID do dispositivo
    """
    print(f"\\n=== MODO BATCH: Criando {count} templates ===")
    
    for i in range(1, count + 1):
        print(f"\\n--- Template {i}/{count} ---")
        template_name = create_action_template_by_marking(
            action_name, 
            i, 
            device_id=device_id
        )
        
        if template_name:
            print(f"✅ Template {i} criado: {template_name}")
        else:
            print(f"❌ Falha ao criar template {i}")
            retry = input("Tentar novamente? (s/n): ").lower()
            if retry == 's':
                i -= 1  # Repete este template
```

### 4. **Adicionar Detecção de Scroll Incremental**
**Problema:** Para rallys, cada item precisa de scroll incremental
**Solução:** Calcular scroll automaticamente baseado na posição

```python
def calculate_scroll_for_position(position_index, base_scroll=300):
    """
    Calcula scroll necessário para cada posição na lista
    
    Args:
        position_index: Índice da posição (0-based)
        base_scroll: Scroll base em ms
        
    Returns:
        int: Duração do scroll em ms
    """
    # Primeiras 3 posições: sem scroll
    if position_index < 3:
        return 0
    
    # Posições 4+: scroll incremental
    # Cada posição adicional precisa de mais scroll
    return base_scroll * (position_index - 2)
```

### 5. **Melhorar Feedback Visual**
**Problema:** Difícil saber se está funcionando
**Solução:** Adicionar mais feedback visual

```python
# Adicionar barra de progresso
def show_progress(current, total, action):
    """Mostra barra de progresso"""
    percent = (current / total) * 100
    bar = "█" * int(percent / 5) + "░" * (20 - int(percent / 5))
    print(f"\\r[{bar}] {percent:.1f}% - {action}", end="", flush=True)
```

### 6. **Adicionar Validação de Template**
**Problema:** Não valida se template foi criado corretamente
**Solução:** Testar template imediatamente após criação

```python
def validate_template(template_path, device_id=None):
    """
    Valida se template pode ser encontrado na tela atual
    
    Returns:
        bool: True se template foi encontrado
    """
    from ..core.image_detection import find_image_on_screen
    from ..core.adb_utils import capture_screen
    
    # Captura tela atual
    test_screenshot = "temp_validation.png"
    if not capture_screen(device_id=device_id, output_path=test_screenshot):
        return False
    
    # Tenta encontrar template
    result = find_image_on_screen(test_screenshot, template_path)
    
    # Limpa arquivo temporário
    if os.path.exists(test_screenshot):
        os.remove(test_screenshot)
    
    return result is not None
```

### 7. **Adicionar Suporte a Configuração de Rally**
**Problema:** Rallys têm padrão específico
**Solução:** Modo específico para rallys

```python
def create_rally_templates(action_name="entrar_rallys", max_rallys=11, device_id=None):
    """
    Modo específico para criar templates de rallys
    
    Args:
        action_name: Nome da ação (padrão: entrar_rallys)
        max_rallys: Número máximo de rallys (padrão: 11)
        device_id: ID do dispositivo
    """
    print("\\n" + "="*60)
    print("  🎯 MODO RALLY - Criação de Templates")
    print("="*60)
    print(f"\\nVamos criar templates para até {max_rallys} rallys")
    print("\\n📋 INSTRUÇÕES:")
    print("1. Navegue até a tela de rallys")
    print("2. Certifique-se de que há rallys disponíveis")
    print("3. Vamos criar um template para cada rally visível")
    print("\\n⚠️  IMPORTANTE:")
    print("- Apenas as 3 primeiras posições ficam visíveis")
    print("- Rallys 4+ precisarão de scroll automático")
    print("- O scroll será configurado automaticamente")
    
    input("\\nPressione Enter quando estiver pronto...")
    
    action_folder = os.path.join("backend", "actions", "templates", action_name)
    if not os.path.exists(action_folder):
        os.makedirs(action_folder)
    
    sequence = []
    
    for i in range(1, max_rallys + 1):
        print(f"\\n{'='*60}")
        print(f"  RALLY {i}/{max_rallys}")
        print("="*60)
        
        # Criar template
        template_name = create_action_template_by_marking(
            action_name,
            i,
            device_id=device_id
        )
        
        if not template_name:
            print(f"❌ Falha ao criar template para rally {i}")
            continue_anyway = input("Continuar mesmo assim? (s/n): ").lower()
            if continue_anyway != 's':
                break
            continue
        
        # Calcular scroll necessário
        scroll_duration = calculate_scroll_for_position(i - 1, base_scroll=300)
        
        # Criar configuração do passo
        step_config = {
            "name": f"Passo {i}: Rally {i}",
            "type": "template",
            "template_file": template_name,
            "action_on_found": "click",
            "click_delay": 0.5,
            "click_offset": [0, 0],
            "max_attempts": 5,
            "attempt_delay": 1.0,
            "initial_delay": 2.0
        }
        
        # Adicionar scroll se necessário
        if scroll_duration > 0:
            step_config["action_before_find"] = {
                "type": "scroll",
                "direction": "up",
                "duration_ms": scroll_duration,
                "delay_after_scroll": 1.5
            }
            print(f"✅ Scroll configurado: {scroll_duration}ms")
        
        sequence.append(step_config)
        print(f"✅ Rally {i} configurado!")
        
        # Perguntar se quer continuar
        if i < max_rallys:
            continue_next = input(f"\\nCriar template para rally {i+1}? (s/n): ").lower()
            if continue_next != 's':
                break
    
    # Salvar sequence.json
    sequence_path = os.path.join(action_folder, "sequence.json")
    with open(sequence_path, 'w', encoding='utf-8') as f:
        json.dump(sequence, f, indent=4)
    
    print(f"\\n{'='*60}")
    print("  ✅ CONFIGURAÇÃO DE RALLYS CONCLUÍDA!")
    print("="*60)
    print(f"\\n📊 Resumo:")
    print(f"   - Templates criados: {len(sequence)}")
    print(f"   - Arquivo salvo: {sequence_path}")
    print(f"\\n🎯 Próximo passo:")
    print(f"   - Teste com: python backend/utils/teste_rally.py")
```

---

## 🎯 RECOMENDAÇÃO

**Para a funcionalidade de Rallys, sugiro:**

1. ✅ **Usar o script atual** - Está bom para criar templates
2. ✅ **Adicionar função específica** - `create_rally_templates()` 
3. ✅ **Configurar scrolls automaticamente** - Baseado na posição
4. ✅ **Criar script de teste** - Similar ao `teste_ciclo_uma_conta.py`

---

## 📝 PRÓXIMOS PASSOS

1. **Você cria os templates** usando o script atual
2. **Eu implemento** as melhorias sugeridas
3. **Criamos** o script `entrar_rallys.py`
4. **Testamos** com rallys reais

**Quer que eu implemente as melhorias agora ou prefere criar os templates primeiro?** 🤔
