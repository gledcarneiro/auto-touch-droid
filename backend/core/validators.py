"""
Validadores de Schemas JSON
Valida arquivos de configuração e sequências de ações
"""
from jsonschema import validate, ValidationError as JSONSchemaValidationError, Draft7Validator
from typing import Dict, List, Any, Tuple
import json
from pathlib import Path

from backend.core.exceptions import SequenceValidationError, SchemaValidationError
from backend.core.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# Schemas JSON
# ============================================================================

SEQUENCE_STEP_SCHEMA = {
    "type": "object",
    "required": ["name", "type"],
    "properties": {
        "name": {
            "type": "string",
            "minLength": 1,
            "description": "Nome descritivo do passo"
        },
        "type": {
            "type": "string",
            "enum": ["template", "scroll", "delay", "conditional", "loop"],
            "description": "Tipo de ação"
        },
        # Propriedades para type: template
        "template_file": {
            "type": "string",
            "description": "Nome do arquivo de template (para type=template)"
        },
        "action_on_found": {
            "type": "string",
            "enum": ["click", "none", "swipe"],
            "description": "Ação ao encontrar template"
        },
        "click_delay": {
            "type": "number",
            "minimum": 0,
            "description": "Delay após clicar (segundos)"
        },
        "click_offset": {
            "type": "array",
            "items": {"type": "number"},
            "minItems": 2,
            "maxItems": 2,
            "description": "Offset do clique [x, y]"
        },
        "max_attempts": {
            "type": "integer",
            "minimum": 1,
            "description": "Número máximo de tentativas"
        },
        "attempt_delay": {
            "type": "number",
            "minimum": 0,
            "description": "Delay entre tentativas (segundos)"
        },
        "initial_delay": {
            "type": "number",
            "minimum": 0,
            "description": "Delay inicial antes de buscar (segundos)"
        },
        # Propriedades para type: scroll
        "direction": {
            "type": "string",
            "enum": ["up", "down", "left", "right"],
            "description": "Direção do scroll"
        },
        "duration_ms": {
            "type": "integer",
            "minimum": 100,
            "description": "Duração do scroll (milissegundos)"
        },
        # Propriedades para type: delay
        "duration": {
            "type": "number",
            "minimum": 0,
            "description": "Duração do delay (segundos)"
        },
        # Propriedades para action_before_find
        "action_before_find": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": ["scroll", "delay"]},
                "direction": {"type": "string", "enum": ["up", "down", "left", "right"]},
                "duration_ms": {"type": "integer", "minimum": 100},
                "delay_after_scroll": {"type": "number", "minimum": 0}
            }
        },
        # Propriedades para ROI (Region of Interest)
        "roi": {
            "type": "array",
            "items": {"type": "integer"},
            "minItems": 4,
            "maxItems": 4,
            "description": "Região de interesse [x, y, width, height]"
        },
        # Propriedades para detecção avançada
        "threshold": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "Threshold de confiança para detecção"
        },
        "multiscale": {
            "type": "boolean",
            "description": "Usar detecção em múltiplas escalas"
        },
        "scales": {
            "type": "array",
            "items": {"type": "number", "minimum": 0.1},
            "description": "Escalas para detecção multiscale"
        }
    },
    "allOf": [
        {
            # Se type=template, template_file é obrigatório
            "if": {"properties": {"type": {"const": "template"}}},
            "then": {"required": ["template_file"]}
        },
        {
            # Se type=scroll, direction é obrigatório
            "if": {"properties": {"type": {"const": "scroll"}}},
            "then": {"required": ["direction"]}
        },
        {
            # Se type=delay, duration é obrigatório
            "if": {"properties": {"type": {"const": "delay"}}},
            "then": {"required": ["duration"]}
        }
    ]
}

SEQUENCE_SCHEMA = {
    "type": "array",
    "items": SEQUENCE_STEP_SCHEMA,
    "minItems": 1,
    "description": "Sequência de ações"
}

ACCOUNT_SCHEMA = {
    "type": "object",
    "required": ["name"],
    "properties": {
        "name": {
            "type": "string",
            "pattern": "^login_[a-zA-Z0-9_]+$",
            "description": "Nome da conta (deve começar com 'login_')"
        },
        "email": {
            "type": "string",
            "format": "email",
            "description": "Email da conta (opcional)"
        },
        "index": {
            "type": "integer",
            "minimum": 0,
            "description": "Índice da conta na lista"
        },
        "enabled": {
            "type": "boolean",
            "description": "Se a conta está habilitada"
        }
    }
}

ACCOUNTS_CONFIG_SCHEMA = {
    "type": "array",
    "items": ACCOUNT_SCHEMA,
    "minItems": 1,
    "description": "Lista de contas"
}


# ============================================================================
# Validadores
# ============================================================================

class SequenceValidator:
    """Validador de arquivos sequence.json"""
    
    @staticmethod
    def validate(sequence_data: List[Dict], action_name: str = None) -> Tuple[bool, List[str]]:
        """
        Valida uma sequência de ações
        
        Args:
            sequence_data: Dados da sequência (lista de passos)
            action_name: Nome da ação (para mensagens de erro)
        
        Returns:
            Tupla (is_valid, errors)
        
        Raises:
            SequenceValidationError: Se a validação falhar
        """
        errors = []
        
        # Validar schema JSON
        validator = Draft7Validator(SEQUENCE_SCHEMA)
        schema_errors = list(validator.iter_errors(sequence_data))
        
        for error in schema_errors:
            path = ".".join(str(p) for p in error.path) if error.path else "root"
            errors.append(f"{path}: {error.message}")
        
        # Validações adicionais
        for i, step in enumerate(sequence_data):
            step_errors = SequenceValidator._validate_step(step, i)
            errors.extend(step_errors)
        
        if errors:
            if action_name:
                raise SequenceValidationError(action_name, errors)
            return False, errors
        
        logger.debug(f"✓ Sequência validada com sucesso ({len(sequence_data)} passos)")
        return True, []
    
    @staticmethod
    def _validate_step(step: Dict, index: int) -> List[str]:
        """Valida um passo individual"""
        errors = []
        step_type = step.get('type')
        
        # Validar tipo template
        if step_type == 'template':
            if 'action_on_found' in step:
                action = step['action_on_found']
                if action == 'click' and 'click_offset' in step:
                    offset = step['click_offset']
                    if len(offset) != 2:
                        errors.append(f"Passo {index}: click_offset deve ter 2 elementos [x, y]")
        
        # Validar ROI se presente
        if 'roi' in step:
            roi = step['roi']
            if len(roi) != 4:
                errors.append(f"Passo {index}: ROI deve ter 4 elementos [x, y, width, height]")
            elif any(v < 0 for v in roi):
                errors.append(f"Passo {index}: ROI não pode ter valores negativos")
        
        # Validar scales se multiscale
        if step.get('multiscale') and 'scales' not in step:
            errors.append(f"Passo {index}: multiscale=true requer campo 'scales'")
        
        return errors
    
    @staticmethod
    def validate_file(file_path: Path, action_name: str = None) -> Tuple[bool, List[str]]:
        """
        Valida um arquivo sequence.json
        
        Args:
            file_path: Caminho para o arquivo
            action_name: Nome da ação
        
        Returns:
            Tupla (is_valid, errors)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Verificar se é lista ou dicionário com chave 'steps'
            if isinstance(data, dict):
                if 'steps' in data:
                    sequence_data = data['steps']
                else:
                    return False, ["Arquivo deve conter lista de passos ou objeto com chave 'steps'"]
            elif isinstance(data, list):
                sequence_data = data
            else:
                return False, ["Arquivo deve conter lista ou objeto"]
            
            return SequenceValidator.validate(sequence_data, action_name)
        
        except json.JSONDecodeError as e:
            return False, [f"Erro ao parsear JSON: {str(e)}"]
        except Exception as e:
            return False, [f"Erro ao ler arquivo: {str(e)}"]


class AccountsValidator:
    """Validador de configuração de contas"""
    
    @staticmethod
    def validate(accounts_data: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Valida lista de contas
        
        Args:
            accounts_data: Lista de contas
        
        Returns:
            Tupla (is_valid, errors)
        """
        errors = []
        
        # Validar schema JSON
        try:
            validate(instance=accounts_data, schema=ACCOUNTS_CONFIG_SCHEMA)
        except JSONSchemaValidationError as e:
            errors.append(f"Erro de schema: {e.message}")
            return False, errors
        
        # Validar nomes únicos
        names = [acc.get('name') for acc in accounts_data]
        duplicates = [name for name in names if names.count(name) > 1]
        if duplicates:
            errors.append(f"Nomes de conta duplicados: {set(duplicates)}")
        
        # Validar índices únicos (se presentes)
        indices = [acc.get('index') for acc in accounts_data if 'index' in acc]
        if indices:
            duplicate_indices = [idx for idx in indices if indices.count(idx) > 1]
            if duplicate_indices:
                errors.append(f"Índices duplicados: {set(duplicate_indices)}")
        
        if errors:
            return False, errors
        
        logger.debug(f"✓ Configuração de contas validada ({len(accounts_data)} contas)")
        return True, []


# ============================================================================
# Funções Helper
# ============================================================================

def validate_sequence_file(action_name: str, file_path: Path = None) -> bool:
    """
    Valida arquivo sequence.json de uma ação
    
    Args:
        action_name: Nome da ação
        file_path: Caminho do arquivo (se None, usa caminho padrão)
    
    Returns:
        True se válido
    
    Raises:
        SequenceValidationError: Se inválido
    """
    if file_path is None:
        from backend.config.settings import settings
        file_path = settings.get_sequence_path(action_name)
    
    is_valid, errors = SequenceValidator.validate_file(file_path, action_name)
    
    if not is_valid:
        raise SequenceValidationError(action_name, errors)
    
    return True


def validate_accounts_config(accounts: List[Dict]) -> bool:
    """
    Valida configuração de contas
    
    Args:
        accounts: Lista de contas
    
    Returns:
        True se válido
    
    Raises:
        SchemaValidationError: Se inválido
    """
    is_valid, errors = AccountsValidator.validate(accounts)
    
    if not is_valid:
        raise SchemaValidationError('accounts_config', errors)
    
    return True


if __name__ == '__main__':
    # Teste de validadores
    print("Testando validadores...\n")
    
    # Teste 1: Sequência válida
    valid_sequence = [
        {
            "name": "Passo 1",
            "type": "template",
            "template_file": "01_google.png",
            "action_on_found": "click",
            "max_attempts": 5
        },
        {
            "name": "Passo 2",
            "type": "scroll",
            "direction": "up",
            "duration_ms": 500
        },
        {
            "name": "Passo 3",
            "type": "delay",
            "duration": 2.0
        }
    ]
    
    is_valid, errors = SequenceValidator.validate(valid_sequence)
    print(f"✓ Sequência válida: {is_valid}")
    if errors:
        print(f"  Erros: {errors}")
    print()
    
    # Teste 2: Sequência inválida
    invalid_sequence = [
        {
            "name": "Passo inválido",
            "type": "template"
            # Faltando template_file
        }
    ]
    
    is_valid, errors = SequenceValidator.validate(invalid_sequence)
    print(f"✓ Sequência inválida detectada: {not is_valid}")
    print(f"  Erros: {errors}")
    print()
    
    # Teste 3: Contas válidas
    valid_accounts = [
        {"name": "login_gled"},
        {"name": "login_inf"},
        {"name": "login_cav"}
    ]
    
    is_valid, errors = AccountsValidator.validate(valid_accounts)
    print(f"✓ Contas válidas: {is_valid}")
    print()
    
    # Teste 4: Contas inválidas (duplicadas)
    invalid_accounts = [
        {"name": "login_gled"},
        {"name": "login_gled"}  # Duplicado
    ]
    
    is_valid, errors = AccountsValidator.validate(invalid_accounts)
    print(f"✓ Contas inválidas detectadas: {not is_valid}")
    print(f"  Erros: {errors}")
    print()
    
    print("✅ Todos os testes de validação concluídos!")
