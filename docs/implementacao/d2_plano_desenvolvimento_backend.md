# 🚀 PLANO DE DESENVOLVIMENTO - BACKEND

**Data de Início:** 24/11/2025  
**Foco:** Continuidade e Novas Funcionalidades  
**Objetivo:** Tornar o backend robusto, testável e extensível

---

## 📋 FASE 1: ESTABILIZAÇÃO E MELHORIAS IMEDIATAS

### Sprint 1: Infraestrutura Base (Semana 1)

#### 1.1 Sistema de Configuração Centralizado ✅
**Arquivo:** `backend/config/settings.py`
- Centralizar todas as configurações
- Suporte a variáveis de ambiente (.env)
- Validação de configurações
- Configurações por ambiente (dev/prod)

#### 1.2 Sistema de Logging Estruturado ✅
**Arquivo:** `backend/core/logger.py`
- Logging com níveis (DEBUG, INFO, WARNING, ERROR)
- Rotação de arquivos
- Formatação estruturada
- Logs separados por módulo

#### 1.3 Validação de Schemas JSON ✅
**Arquivo:** `backend/core/validators.py`
- Validar sequence.json
- Validar accounts_config
- Schemas com jsonschema
- Mensagens de erro claras

#### 1.4 Tratamento de Erros Robusto ✅
**Arquivo:** `backend/core/exceptions.py`
- Exceções customizadas
- Hierarquia de exceções
- Mensagens de erro descritivas
- Recovery automático quando possível

---

## 📋 FASE 2: NOVAS FUNCIONALIDADES

### Sprint 2: Detecção Avançada (Semana 2)

#### 2.1 Multi-Template Matching
**Funcionalidade:** Buscar múltiplos templates simultaneamente
```python
def find_multiple_templates(screenshot_path, template_paths, threshold=0.8):
    """Encontra múltiplos templates na mesma screenshot"""
    results = []
    for template_path in template_paths:
        result = find_image_on_screen(screenshot_path, template_path, threshold)
        if result:
            results.append({
                'template': template_path,
                'position': result,
                'confidence': calculate_confidence(result)
            })
    return results
```

#### 2.2 Detecção com Múltiplas Escalas
**Funcionalidade:** Detectar templates em diferentes tamanhos
```python
def find_image_multiscale(screenshot_path, template_path, scales=[0.8, 1.0, 1.2]):
    """Busca template em múltiplas escalas"""
    best_match = None
    best_confidence = 0
    
    for scale in scales:
        # Redimensionar template
        # Buscar
        # Comparar confiança
        pass
    
    return best_match
```

#### 2.3 Detecção por Região de Interesse (ROI)
**Funcionalidade:** Limitar busca a áreas específicas
```python
def find_image_in_roi(screenshot_path, template_path, roi):
    """
    Busca template apenas em região específica
    roi: (x, y, width, height)
    """
    # Recortar screenshot para ROI
    # Buscar template
    # Ajustar coordenadas para screenshot completo
    pass
```

#### 2.4 Cache de Templates
**Funcionalidade:** Evitar recarregar templates repetidamente
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def load_template_cached(template_path):
    """Carrega template com cache"""
    return cv2.imread(template_path)
```

### Sprint 3: Ações Avançadas (Semana 3)

#### 3.1 Gestos Customizados
**Funcionalidade:** Swipe, pinch, long press
```python
def simulate_swipe(start_pos, end_pos, duration_ms=500, device_id=None):
    """Simula gesto de swipe"""
    pass

def simulate_long_press(x, y, duration_ms=1000, device_id=None):
    """Simula long press"""
    pass

def simulate_pinch(center, scale_factor, device_id=None):
    """Simula pinch to zoom"""
    pass
```

#### 3.2 Ações Condicionais
**Funcionalidade:** Executar ações baseadas em condições
```json
{
    "name": "Verificar e coletar",
    "type": "conditional",
    "condition": {
        "type": "template_exists",
        "template_file": "recurso_disponivel.png"
    },
    "actions_if_true": [
        {"type": "template", "template_file": "coletar.png", "action_on_found": "click"}
    ],
    "actions_if_false": [
        {"type": "delay", "duration": 5.0}
    ]
}
```

#### 3.3 Loops e Repetições
**Funcionalidade:** Repetir ações até condição
```json
{
    "name": "Coletar todos os recursos",
    "type": "loop",
    "max_iterations": 10,
    "break_condition": {
        "type": "template_not_found",
        "template_file": "recurso_disponivel.png"
    },
    "actions": [
        {"type": "template", "template_file": "recurso.png", "action_on_found": "click"},
        {"type": "delay", "duration": 2.0}
    ]
}
```

#### 3.4 Variáveis e Estado
**Funcionalidade:** Manter estado entre ações
```python
class ActionContext:
    """Contexto de execução com variáveis"""
    def __init__(self):
        self.variables = {}
        self.history = []
        self.counters = {}
    
    def set_var(self, name, value):
        self.variables[name] = value
    
    def get_var(self, name, default=None):
        return self.variables.get(name, default)
    
    def increment_counter(self, name):
        self.counters[name] = self.counters.get(name, 0) + 1
```

### Sprint 4: Performance e Otimização (Semana 4)

#### 4.1 Processamento Paralelo
**Funcionalidade:** Executar múltiplas contas em paralelo
```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def execute_login_parallel(accounts, max_workers=3):
    """Executa login em múltiplas contas paralelamente"""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(execute_login_for_account, account): account
            for account in accounts
        }
        
        for future in as_completed(futures):
            account = futures[future]
            try:
                result = future.result()
                print(f"✅ {account['name']}: {result}")
            except Exception as e:
                print(f"❌ {account['name']}: {e}")
```

#### 4.2 Otimização de Capturas
**Funcionalidade:** Reduzir capturas desnecessárias
```python
class ScreenshotManager:
    """Gerencia capturas de tela com cache"""
    def __init__(self, cache_duration=1.0):
        self.cache = {}
        self.cache_duration = cache_duration
    
    def get_screenshot(self, device_id=None, force_new=False):
        """Retorna screenshot do cache ou captura nova"""
        cache_key = device_id or 'default'
        now = time.time()
        
        if not force_new and cache_key in self.cache:
            screenshot, timestamp = self.cache[cache_key]
            if now - timestamp < self.cache_duration:
                return screenshot
        
        # Capturar nova screenshot
        screenshot = capture_screen(device_id)
        self.cache[cache_key] = (screenshot, now)
        return screenshot
```

#### 4.3 Métricas de Performance
**Funcionalidade:** Monitorar performance das ações
```python
import time
from contextlib import contextmanager

class PerformanceMonitor:
    """Monitora performance de execuções"""
    def __init__(self):
        self.metrics = {}
    
    @contextmanager
    def measure(self, operation_name):
        """Context manager para medir tempo"""
        start = time.time()
        try:
            yield
        finally:
            duration = time.time() - start
            self._record_metric(operation_name, duration)
    
    def _record_metric(self, name, duration):
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(duration)
    
    def get_stats(self, name):
        """Retorna estatísticas de uma operação"""
        if name not in self.metrics:
            return None
        
        durations = self.metrics[name]
        return {
            'count': len(durations),
            'avg': sum(durations) / len(durations),
            'min': min(durations),
            'max': max(durations)
        }
```

---

## 📋 FASE 3: FUNCIONALIDADES AVANÇADAS

### Sprint 5: Sistema de Plugins (Semana 5)

#### 5.1 Interface de Plugin
```python
from abc import ABC, abstractmethod

class ActionPlugin(ABC):
    """Interface base para plugins de ação"""
    
    @abstractmethod
    def get_name(self) -> str:
        """Nome do plugin"""
        pass
    
    @abstractmethod
    def execute(self, context: ActionContext, params: dict) -> bool:
        """Executa a ação do plugin"""
        pass
    
    @abstractmethod
    def validate_params(self, params: dict) -> bool:
        """Valida parâmetros do plugin"""
        pass
```

#### 5.2 Gerenciador de Plugins
```python
class PluginManager:
    """Gerencia plugins de ação"""
    def __init__(self):
        self.plugins = {}
    
    def register_plugin(self, plugin: ActionPlugin):
        """Registra um novo plugin"""
        name = plugin.get_name()
        self.plugins[name] = plugin
    
    def execute_plugin(self, name: str, context: ActionContext, params: dict):
        """Executa um plugin"""
        if name not in self.plugins:
            raise ValueError(f"Plugin '{name}' não encontrado")
        
        plugin = self.plugins[name]
        if not plugin.validate_params(params):
            raise ValueError(f"Parâmetros inválidos para plugin '{name}'")
        
        return plugin.execute(context, params)
```

### Sprint 6: API REST (Semana 6)

#### 6.1 Servidor Flask
```python
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/actions', methods=['GET'])
def list_actions():
    """Lista todas as ações disponíveis"""
    actions = get_available_actions()
    return jsonify({'actions': actions})

@app.route('/api/actions/execute', methods=['POST'])
def execute_action():
    """Executa uma ação"""
    data = request.json
    action_name = data.get('action_name')
    device_id = data.get('device_id')
    
    result = execultar_acoes(action_name, device_id)
    return jsonify({'success': result})

@app.route('/api/status', methods=['GET'])
def get_status():
    """Retorna status do sistema"""
    return jsonify({
        'backend': 'online',
        'adb_connected': check_adb_connection(),
        'actions_count': len(get_available_actions())
    })
```

#### 6.2 WebSocket para Execução em Tempo Real
```python
from flask_socketio import SocketIO, emit

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('execute_action')
def handle_execute_action(data):
    """Executa ação e envia atualizações em tempo real"""
    action_name = data.get('action_name')
    
    # Callback para enviar progresso
    def progress_callback(step, progress):
        emit('action_progress', {
            'step': step,
            'progress': progress
        })
    
    result = execultar_acoes(action_name, progress_callback=progress_callback)
    emit('action_complete', {'success': result})
```

### Sprint 7: Machine Learning (Semana 7-8)

#### 7.1 Detecção com YOLO (Opcional)
```python
# Detecção de objetos mais robusta
import torch
from ultralytics import YOLO

class YOLODetector:
    """Detector usando YOLO para elementos de UI"""
    def __init__(self, model_path='yolov8n.pt'):
        self.model = YOLO(model_path)
    
    def detect_ui_elements(self, screenshot_path):
        """Detecta elementos de UI na screenshot"""
        results = self.model(screenshot_path)
        
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                detections.append({
                    'class': result.names[int(box.cls)],
                    'confidence': float(box.conf),
                    'bbox': box.xyxy[0].tolist()
                })
        
        return detections
```

#### 7.2 Aprendizado de Padrões
```python
class PatternLearner:
    """Aprende padrões de execução bem-sucedida"""
    def __init__(self):
        self.successful_patterns = []
        self.failed_patterns = []
    
    def record_execution(self, action_sequence, success):
        """Registra execução para aprendizado"""
        pattern = self._extract_pattern(action_sequence)
        
        if success:
            self.successful_patterns.append(pattern)
        else:
            self.failed_patterns.append(pattern)
    
    def suggest_improvements(self, action_sequence):
        """Sugere melhorias baseadas em padrões aprendidos"""
        # Analisar padrões bem-sucedidos
        # Comparar com sequência atual
        # Sugerir ajustes
        pass
```

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### ✅ Prioridade Alta (Fazer Primeiro)

- [ ] **Sistema de Configuração** (`backend/config/settings.py`)
- [ ] **Sistema de Logging** (`backend/core/logger.py`)
- [ ] **Validação de Schemas** (`backend/core/validators.py`)
- [ ] **Exceções Customizadas** (`backend/core/exceptions.py`)
- [ ] **Testes Unitários Básicos** (`tests/unit/`)

### 🔄 Prioridade Média (Fazer em Seguida)

- [ ] **Multi-Template Matching**
- [ ] **Cache de Templates**
- [ ] **Gestos Customizados**
- [ ] **Ações Condicionais**
- [ ] **Processamento Paralelo**

### 💡 Prioridade Baixa (Fazer Depois)

- [ ] **Sistema de Plugins**
- [ ] **API REST**
- [ ] **WebSocket**
- [ ] **Machine Learning**
- [ ] **Dashboard Web**

---

## 🎯 PRÓXIMOS PASSOS IMEDIATOS

### Hoje (24/11/2025):
1. ✅ Criar estrutura de pastas para novos módulos
2. ✅ Implementar sistema de configuração
3. ✅ Implementar sistema de logging
4. ✅ Criar exceções customizadas

### Esta Semana:
1. Implementar validação de schemas
2. Adicionar testes unitários
3. Refatorar código existente para usar novos sistemas
4. Documentar novos módulos

### Próxima Semana:
1. Implementar detecção avançada
2. Adicionar gestos customizados
3. Criar ações condicionais
4. Otimizar performance

---

## 📊 MÉTRICAS DE SUCESSO

- ✅ Código com 70%+ de cobertura de testes
- ✅ Logs estruturados em todos os módulos
- ✅ Configurações centralizadas
- ✅ Tempo de detecção < 500ms
- ✅ Suporte a 5+ novos tipos de ação
- ✅ API REST funcional
- ✅ Documentação completa

---

**Vamos começar! 🚀**
