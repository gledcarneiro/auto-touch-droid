"""
Exceções Customizadas
Define hierarquia de exceções para tratamento de erros específicos do projeto
"""


class AutoTouchError(Exception):
    """Exceção base para todos os erros do Auto Touch Droid"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self):
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


# ============================================================================
# Exceções de ADB
# ============================================================================

class ADBError(AutoTouchError):
    """Erro relacionado ao ADB"""
    pass


class ADBConnectionError(ADBError):
    """Erro de conexão com dispositivo via ADB"""
    pass


class ADBCommandError(ADBError):
    """Erro ao executar comando ADB"""
    def __init__(self, command: str, return_code: int, output: str = ""):
        super().__init__(
            f"Comando ADB falhou: {command}",
            {"return_code": return_code, "output": output}
        )
        self.command = command
        self.return_code = return_code
        self.output = output


class DeviceNotFoundError(ADBError):
    """Dispositivo não encontrado"""
    def __init__(self, device_id: str = None):
        msg = f"Dispositivo não encontrado: {device_id}" if device_id else "Nenhum dispositivo encontrado"
        super().__init__(msg, {"device_id": device_id})


class ScreenCaptureError(ADBError):
    """Erro ao capturar tela"""
    pass


# ============================================================================
# Exceções de Detecção de Imagem
# ============================================================================

class DetectionError(AutoTouchError):
    """Erro relacionado à detecção de imagem"""
    pass


class TemplateNotFoundError(DetectionError):
    """Template não encontrado após todas as tentativas"""
    def __init__(self, template_name: str, attempts: int):
        super().__init__(
            f"Template não encontrado: {template_name}",
            {"template_name": template_name, "attempts": attempts}
        )
        self.template_name = template_name
        self.attempts = attempts


class TemplateLoadError(DetectionError):
    """Erro ao carregar arquivo de template"""
    def __init__(self, template_path: str, reason: str = ""):
        super().__init__(
            f"Erro ao carregar template: {template_path}",
            {"template_path": template_path, "reason": reason}
        )
        self.template_path = template_path


class InvalidTemplateError(DetectionError):
    """Template inválido ou corrompido"""
    pass


class ScreenshotLoadError(DetectionError):
    """Erro ao carregar screenshot"""
    pass


# ============================================================================
# Exceções de Ações
# ============================================================================

class ActionError(AutoTouchError):
    """Erro relacionado à execução de ações"""
    pass


class ActionNotFoundError(ActionError):
    """Ação não encontrada"""
    def __init__(self, action_name: str):
        super().__init__(
            f"Ação não encontrada: {action_name}",
            {"action_name": action_name}
        )
        self.action_name = action_name


class ActionExecutionError(ActionError):
    """Erro durante execução de ação"""
    def __init__(self, action_name: str, step: str = None, reason: str = ""):
        details = {"action_name": action_name}
        if step:
            details["step"] = step
        if reason:
            details["reason"] = reason
        
        msg = f"Erro ao executar ação: {action_name}"
        if step:
            msg += f" (Passo: {step})"
        
        super().__init__(msg, details)
        self.action_name = action_name
        self.step = step


class ActionTimeoutError(ActionError):
    """Timeout durante execução de ação"""
    def __init__(self, action_name: str, timeout: float):
        super().__init__(
            f"Timeout ao executar ação: {action_name}",
            {"action_name": action_name, "timeout": timeout}
        )


class InvalidActionStepError(ActionError):
    """Passo de ação inválido"""
    def __init__(self, step_name: str, reason: str):
        super().__init__(
            f"Passo de ação inválido: {step_name}",
            {"step_name": step_name, "reason": reason}
        )


# ============================================================================
# Exceções de Configuração
# ============================================================================

class ConfigurationError(AutoTouchError):
    """Erro de configuração"""
    pass


class InvalidConfigError(ConfigurationError):
    """Configuração inválida"""
    pass


class MissingConfigError(ConfigurationError):
    """Configuração obrigatória ausente"""
    def __init__(self, config_key: str):
        super().__init__(
            f"Configuração obrigatória ausente: {config_key}",
            {"config_key": config_key}
        )


# ============================================================================
# Exceções de Validação
# ============================================================================

class ValidationError(AutoTouchError):
    """Erro de validação"""
    pass


class SequenceValidationError(ValidationError):
    """Erro de validação de sequence.json"""
    def __init__(self, action_name: str, errors: list):
        super().__init__(
            f"Erros de validação em sequence.json: {action_name}",
            {"action_name": action_name, "errors": errors}
        )
        self.errors = errors


class SchemaValidationError(ValidationError):
    """Erro de validação de schema JSON"""
    def __init__(self, schema_name: str, errors: list):
        super().__init__(
            f"Erros de validação de schema: {schema_name}",
            {"schema_name": schema_name, "errors": errors}
        )


# ============================================================================
# Exceções de Arquivo
# ============================================================================

class FileError(AutoTouchError):
    """Erro relacionado a arquivos"""
    pass


class FileNotFoundError(FileError):
    """Arquivo não encontrado"""
    def __init__(self, file_path: str):
        super().__init__(
            f"Arquivo não encontrado: {file_path}",
            {"file_path": file_path}
        )


class FileReadError(FileError):
    """Erro ao ler arquivo"""
    pass


class FileWriteError(FileError):
    """Erro ao escrever arquivo"""
    pass


# ============================================================================
# Exceções de Conta
# ============================================================================

class AccountError(AutoTouchError):
    """Erro relacionado a contas"""
    pass


class AccountNotFoundError(AccountError):
    """Conta não encontrada"""
    def __init__(self, account_name: str):
        super().__init__(
            f"Conta não encontrada: {account_name}",
            {"account_name": account_name}
        )


class InvalidAccountError(AccountError):
    """Configuração de conta inválida"""
    pass


# ============================================================================
# Funções Helper
# ============================================================================

def handle_exception(exception: Exception, logger=None, reraise: bool = True):
    """
    Handler genérico para exceções
    
    Args:
        exception: Exceção capturada
        logger: Logger para registrar o erro
        reraise: Se True, relança a exceção após logging
    """
    if logger:
        if isinstance(exception, AutoTouchError):
            logger.error(f"❌ {exception}")
            if exception.details:
                logger.debug(f"Detalhes: {exception.details}")
        else:
            logger.error(f"❌ Erro inesperado: {type(exception).__name__}: {str(exception)}")
            logger.debug("Stack trace:", exc_info=True)
    
    if reraise:
        raise exception


def wrap_adb_error(func):
    """
    Decorator para capturar e converter erros de ADB
    
    Exemplo:
        @wrap_adb_error
        def my_adb_function():
            # código que pode gerar erros
            pass
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except subprocess.CalledProcessError as e:
            raise ADBCommandError(
                command=e.cmd,
                return_code=e.returncode,
                output=e.output.decode() if e.output else ""
            )
        except Exception as e:
            if not isinstance(e, AutoTouchError):
                raise ADBError(f"Erro ADB: {str(e)}")
            raise
    
    return wrapper


def wrap_detection_error(func):
    """
    Decorator para capturar e converter erros de detecção
    
    Exemplo:
        @wrap_detection_error
        def my_detection_function():
            # código que pode gerar erros
            pass
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if not isinstance(e, AutoTouchError):
                raise DetectionError(f"Erro de detecção: {str(e)}")
            raise
    
    return wrapper


if __name__ == '__main__':
    # Teste de exceções
    print("Testando exceções customizadas...\n")
    
    # Teste 1: ADBError
    try:
        raise ADBCommandError("adb devices", 1, "error: no devices")
    except ADBCommandError as e:
        print(f"✓ ADBCommandError: {e}")
        print(f"  Details: {e.details}\n")
    
    # Teste 2: TemplateNotFoundError
    try:
        raise TemplateNotFoundError("01_google.png", 5)
    except TemplateNotFoundError as e:
        print(f"✓ TemplateNotFoundError: {e}")
        print(f"  Template: {e.template_name}, Attempts: {e.attempts}\n")
    
    # Teste 3: ActionExecutionError
    try:
        raise ActionExecutionError("fazer_login", "Passo 1", "Template não encontrado")
    except ActionExecutionError as e:
        print(f"✓ ActionExecutionError: {e}")
        print(f"  Details: {e.details}\n")
    
    # Teste 4: SequenceValidationError
    try:
        raise SequenceValidationError("fazer_login", [
            "Campo 'name' obrigatório",
            "Campo 'type' deve ser 'template' ou 'scroll'"
        ])
    except SequenceValidationError as e:
        print(f"✓ SequenceValidationError: {e}")
        print(f"  Errors: {e.errors}\n")
    
    print("✅ Todos os testes de exceções passaram!")
